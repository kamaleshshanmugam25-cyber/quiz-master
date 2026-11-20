import json
import asyncio
import time
import random

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
import redis.asyncio as aioredis
from django.conf import settings

_redis_client = None

def _get_redis():
    global _redis_client
    if _redis_client is None:
        redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/0')
        _redis_client = aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
            retry_on_timeout=True
        )
    return _redis_client


def _sanitize_question_for_player(q):
    if not q:
        return None
    q_copy = dict(q)
    if "choices" in q_copy:
        q_copy["choices"] = [
            {k: v for k, v in dict(c).items() if k != "is_correct"}
            for c in q_copy["choices"]
        ]
    return q_copy

from .models import (
    QuizSession,
    Participant,
    Question,
    Choice,
    AnswerRecord,
)

# =========================================================
# HIGH PERFORMANCE QUIZ CONSUMER
# Optimized for 500+ users
# =========================================================

runtime_sessions = {}

GRAPH_DEBOUNCE_SEC = 0.4
LOBBY_BATCH_SEC = 0.5
MAX_CLIENTS_PER_SESSION = 500


# =========================================================
# SESSION FACTORY
# =========================================================
def _make_session():
    return {
        "current_q": None,
        "counts": {},
        "question_start": None,
        "status": "lobby",
        "last_q": None,
        "last_counts": {},
        "clients": set(),
        "host_channel": None,

        # IMPORTANT:
        # list is faster here than sorted(set())
        "usernames": [],

        "active": True,
        "duration": 10,

        "_graph_task": None,
        "_lobby_task": None,

        # prevent old timers from closing new questions
        "close_task": None,
    }
    
def _init_session(code: str):
    if code not in runtime_sessions:
        runtime_sessions[code] = _make_session()

    return runtime_sessions[code]


def _question_payload(question):
    if not question:
        return None
    return {
        "id": question.id,
        "text": question.text,
        "timer_seconds": question.timer_seconds,
        "order": question.order,
        "image": question.image,
        "choices": [
            {
                "id": choice.id,
                "text": choice.text,
                "is_correct": choice.is_correct,
                "image": choice.image,
            }
            for choice in question.choices.all()
        ],
    }


# =========================================================
# CONSUMER
# =========================================================
class QuizConsumer(AsyncWebsocketConsumer):

    # =====================================================
    # CONNECT
    # =====================================================
    async def connect(self):

        self.session_code = self.scope["url_route"]["kwargs"]["session_code"]
        self.group_name = f"quiz_{self.session_code}"

        self.username = None
        self.is_host = False

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        if self.session_code not in runtime_sessions:
            runtime_sessions[self.session_code] = _make_session()

        rs = runtime_sessions[self.session_code]

        # MAX LIMIT
        if len(rs["clients"]) >= MAX_CLIENTS_PER_SESSION:

            await self.send(text_data=json.dumps({
                "type": "join_denied",
                "message": "Session full"
            }))

            await self.close()
            return

        rs["clients"].add(self.channel_name)

        await self._hydrate_runtime_from_db()
        await self._send_sync_state()

    # =====================================================
    # DISCONNECT
    # =====================================================
    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        rs = runtime_sessions.get(self.session_code)

        if rs:

            rs["clients"].discard(self.channel_name)

            # CLEANUP: Only evict from process memory if session is explicitly ended
            if not rs["clients"] and rs.get("status") == "ended":

                close_task = rs.get("close_task")

                if close_task:
                    close_task.cancel()

                runtime_sessions.pop(self.session_code, None)

    # =====================================================
    # RECEIVE
    # =====================================================
    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
        except:
            return

        action = data.get("action")

        # ==========================================
        # JOIN
        # ==========================================
        if action == "join":
            await self._handle_join(data)

        # ==========================================
        # QUESTION
        # ==========================================
        elif action == "broadcast_question":
            await self._handle_broadcast_question(data)

        elif action == "get_state":
            await self._send_current_state(data.get("username"))

        elif action == "reveal_answer":
            await self._handle_reveal_answer()

        elif action == "show_leaderboard":
            await self._handle_show_leaderboard()

        # ==========================================
        # ANSWER
        # ==========================================
        elif action == "answer":
            await self._handle_answer(data)

        # ==========================================
        # LEAVE / KICK / REMOVE
        # ==========================================
        elif action in ("leave", "kick", "remove_participant"):
            await self._handle_leave(data)

        # ==========================================
        # QUIZ FLOW
        # ==========================================
        elif action == "start_quiz":
            await self._start_quiz()

        elif action == "end_quiz":
            await self._end_quiz()

        elif action == "end_session":
            await self._end_session()

        elif action == "next_question":
            await self._next_question()

        # ==========================================
        # EMOJI / REACTIONS
        # ==========================================
        elif action in ("emoji_reaction", "reaction", "emoji"):
            await self._handle_emoji(data)

        # ==========================================
        # CHAT / KEYWORD
        # ==========================================
        elif action == "chat_message":
            await self._handle_chat_message(data)

        # ==========================================
        # RESUME QUESTION
        # ==========================================
        elif action == "resume_question":
            await self._handle_resume_question()

        # ==========================================
        # PAGINATION
        # ==========================================
        elif action == "get_participants_page":
            await self._send_participants_page(data)

        # ==========================================
        # AVATAR UPDATE
        # ==========================================
        elif action == "avatar_update":
            await self._handle_avatar_update(data)

        # ==========================================
        # PROFILE IMAGE UPDATE
        # ==========================================
        elif action == "profile_image_update":
            await self._handle_profile_image_update(data)

        # ==========================================
        # AVATAR IMAGE URL (server URL, not base64)
        # ==========================================
        elif action == "avatar_image_url":
            await self._handle_avatar_image_url(data)

    # =====================================================
    # JOIN
    # =====================================================
    async def _handle_join(self, data):

        username = (data.get("username") or "Guest").strip()

        avatar_id = int(data.get("avatar_id", 0))

        role = data.get("role", "participant")
        is_host = role == "host"

        rs = runtime_sessions.get(self.session_code)

        if not rs:
            return

        if is_host:
            token = data.get("token") or self.scope.get("cookies", {}).get("token")
            is_valid_host = await self._verify_host_token(token)
            if not is_valid_host:
                await self.send(text_data=json.dumps({
                    "type": "join_denied",
                    "message": "Host authorization failed: valid authentication token required."
                }))
                await self.close(code=4003)
                return
            is_valid = True
        else:
            is_valid = await self._validate_participant(username)

        if not is_valid:

            await self.send(text_data=json.dumps({
                "type": "join_denied",
                "message": "Access denied"
            }))

            await self.close()
            return

        self.username = username
        self.is_host = is_host

        if self.is_host:
            rs["host_channel"] = self.channel_name
            await self.send(text_data=json.dumps({
                "type": "joined",
                "username": username,
                "role": "host"
            }))
            await self._send_sync_state(username)
            return

        if role not in ("participant", "player"):
            await self.send(text_data=json.dumps({
                "type": "join_denied",
                "message": "Invalid participant role"
            }))
            await self.close()
            return

        await self._create_participant_db(
            username,
            avatar_id
        )

        # ==========================================
        # FAST LIST APPEND
        # ==========================================
        if username not in rs["usernames"]:
            rs["usernames"].append(username)

        await self.send(text_data=json.dumps({
            "type": "joined",
            "username": username
        }))

        await self._send_sync_state(username)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "participant_join",
                    "participant": {
                        "username": username,
                        "avatar_id": avatar_id,
                        "score": 0,
                    }
                }
            }
        )

        self._schedule_lobby_update(rs)

        # Synchronize participants globally via Redis
        global_count = len(rs["usernames"])
        try:
            r = _get_redis()
            part_key = f"quiz:{self.session_code}:participants"
            await r.sadd(part_key, username)
            await r.expire(part_key, 7200)
            global_count = await r.scard(part_key)
        except Exception:
            pass

        # lightweight count
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "participant_count",
                    "count": global_count
                }
            }
        )

    # =====================================================
    # QUESTION BROADCAST
    # =====================================================
    async def _handle_broadcast_question(self, data):

        q = data.get("question")

        expires_in = int(
            data.get(
                "expires_in",
                q.get("timer_seconds", 30)
            )
        )

        rs = runtime_sessions.get(self.session_code)

        if not rs:
            return

        q = self._shuffle_question_choices(q)

        # CANCEL OLD TIMER
        old_task = rs.get("close_task")

        if old_task:
            old_task.cancel()

        counts = {
            str(c["id"]): 0
            for c in q["choices"]
        }

        rs["current_q"] = q
        rs["counts"] = counts
        rs["question_start"] = int(time.time() * 1000)
        rs["duration"] = expires_in
        rs["status"] = "question"
        rs["last_q"] = q
        rs["last_counts"] = counts
        await self._set_session_state("question", question_id=q.get("id"), question_index=data.get("question_index"), duration=expires_in)

        # Synchronize question & zero counts in Redis
        try:
            r = _get_redis()
            counts_key = f"quiz:{self.session_code}:counts"
            await r.delete(counts_key)
            if counts:
                await r.hset(counts_key, mapping={k: 0 for k in counts.keys()})
                await r.expire(counts_key, 7200)
            state_key = f"quiz:{self.session_code}:state"
            await r.hset(state_key, mapping={
                "status": "question",
                "question_json": json.dumps(q),
                "expires_in": str(expires_in),
                "duration": str(expires_in),
                "question_start": str(int(time.time() * 1000)),
            })
            await r.expire(state_key, 7200)
        except Exception as e:
            print(f"[Redis sync on broadcast]: {e}")

        # BROADCAST: Sanitize choices for players so is_correct is not leaked
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "question",
                    "question": _sanitize_question_for_player(q),
                    "expires_in": expires_in,
                    "duration": expires_in,
                    "question_index": data.get("question_index", 0),
                    "total_questions": data.get("total_questions", 0),
                }
            }
        )

        # NEW TIMER
        rs["close_task"] = asyncio.create_task(
            self._close_question_after(
                self.session_code,
                expires_in
            )
        )

    # =====================================================
    # ANSWER
    # =====================================================
    async def _handle_answer(self, data):

        selected_choice_id = str(
            data.get("selected_choice_id") or data.get("choice_id") or ""
        )

        # Enforce socket-bound participant identity to prevent player impersonation (BUG-04)
        if not getattr(self, "username", None):
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Unauthenticated connection cannot submit answers."
            }))
            return

        username = self.username

        rt = int(
            data.get("response_time_ms", 0)
        )

        rs = runtime_sessions.get(self.session_code)

        if not rs or not rs.get("current_q") or rs.get("status") != "question":
            # Hydrate from Redis shared state if this worker process was cold
            try:
                r = _get_redis()
                st = await r.hgetall(f"quiz:{self.session_code}:state")
                if st and st.get("status") == "question":
                    if not rs:
                        rs = _init_session(self.session_code)
                    rs["status"] = "question"
                    if "question_json" in st:
                        rs["current_q"] = json.loads(st["question_json"])
            except Exception:
                pass

        if not rs or not rs.get("current_q") or rs.get("status") != "question":
            return

        # Atomic cross-worker vote deduplication via Redis (BUG-05)
        qid = str(rs["current_q"].get("id", ""))
        choice_key_str = str(selected_choice_id)
        try:
            r = _get_redis()
            voted_key = f"quiz:{self.session_code}:voted:{qid}"
            is_new_vote = await r.sadd(voted_key, username)
            if not is_new_vote:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Answer already submitted for this question."
                }))
                return

            counts_key = f"quiz:{self.session_code}:counts"
            await r.hincrby(counts_key, choice_key_str, 1)
            raw_counts = await r.hgetall(counts_key)
            rs["counts"] = {k: int(v) for k, v in raw_counts.items()}
        except Exception as e:
            has_already_voted = await self._has_answered(username, qid)
            if has_already_voted:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Answer already submitted for this question."
                }))
                return
            if selected_choice_id in rs["counts"]:
                rs["counts"][selected_choice_id] += 1

        # background db save
        asyncio.create_task(
            self._persist_answer_task(
                username,
                selected_choice_id,
                rt,
                rs["current_q"]
            )
        )

        self._schedule_graph_update(rs)

    # =====================================================
    # LEAVE
    # =====================================================
    async def _handle_leave(self, data):

        username = data.get("username", "")

        if username:

            asyncio.create_task(
                self._remove_participant_db(username)
            )

            rs = runtime_sessions.get(self.session_code)

            if rs:

                if username in rs["usernames"]:
                    rs["usernames"].remove(username)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "send_json",
                        "payload": {
                            "type": "participant_leave",
                            "username": username,
                        }
                    }
                )

                self._schedule_lobby_update(rs)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "send_json",
                        "payload": {
                            "type": "participant_count",
                            "count": len(rs["usernames"])
                        }
                    }
                )

    # =====================================================
    # EMOJI
    # =====================================================
    async def _handle_emoji(self, data):
        emoji = data.get("emoji")
        username = data.get("username") or getattr(self, "username", None) or "Player"

        if emoji:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send_json",
                    "payload": {
                        "type": "emoji_reaction",
                        "emoji": emoji,
                        "username": str(username),
                        "timestamp": int(time.time() * 1000)
                    }
                }
            )

    # =====================================================
    # CHAT MESSAGE
    # =====================================================
    async def _handle_chat_message(self, data):

        message = data.get("message")
        username = data.get("username", "Host")

        if not message:
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message_event",
                "message": message,
                "username": username,
            }
        )

    async def chat_message_event(self, event):

        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "username": event["username"],
        }))

    # =====================================================
    # RESUME
    # =====================================================
    async def _handle_resume_question(self):

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "resume_question_event",
            }
        )

    async def resume_question_event(self, event):

        await self.send(text_data=json.dumps({
            "type": "resume_question"
        }))

    async def _handle_reveal_answer(self):
        rs = runtime_sessions.get(self.session_code)
        if not rs:
            return

        try:
            r = _get_redis()
            counts_key = f"quiz:{self.session_code}:counts"
            raw_counts = await r.hgetall(counts_key)
            if raw_counts:
                counts = {k: int(v) for k, v in raw_counts.items()}
                rs["counts"] = counts
            else:
                counts = dict(rs.get("last_counts") or rs.get("counts") or {})
            await r.hset(f"quiz:{self.session_code}:state", "status", "answer_reveal")
        except Exception:
            counts = dict(rs.get("last_counts") or rs.get("counts") or {})

        q = rs.get("last_q") or rs.get("current_q")
        rs["status"] = "answer_reveal"
        rs["current_q"] = q
        rs["counts"] = counts
        rs["question_start"] = None
        rs["last_q"] = q
        rs["last_counts"] = counts
        await self._set_session_state("answer_reveal", question_id=q.get("id") if q else None)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "correct_revealed",
                    "question": q,
                    "counts": counts,
                }
            }
        )

    async def _handle_show_leaderboard(self):
        rs = runtime_sessions.get(self.session_code)
        if not rs:
            return

        try:
            r = _get_redis()
            counts_key = f"quiz:{self.session_code}:counts"
            raw_counts = await r.hgetall(counts_key)
            if raw_counts:
                counts = {k: int(v) for k, v in raw_counts.items()}
                rs["counts"] = counts
            else:
                counts = dict(rs.get("last_counts") or rs.get("counts") or {})
            await r.hset(f"quiz:{self.session_code}:state", "status", "answer_reveal")
        except Exception:
            counts = dict(rs.get("last_counts") or rs.get("counts") or {})

        q = rs.get("last_q") or rs.get("current_q")
        rs["status"] = "leaderboard"
        rs["current_q"] = q
        rs["counts"] = counts
        rs["question_start"] = None
        rs["last_q"] = q
        rs["last_counts"] = counts
        await self._set_session_state("leaderboard", question_id=q.get("id") if q else None)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "leaderboard_shown",
                    "question": q,
                    "counts": counts,
                }
            }
        )

    # =====================================================
    # PARTICIPANTS PAGE
    # =====================================================
    async def _send_participants_page(self, data):

        rs = runtime_sessions.get(self.session_code)

        if not rs:
            return

        page = int(data.get("page", 0))

        page_size = max(
            1,
            min(int(data.get("page_size", 50)), 200)
        )

        names = rs["usernames"]

        total = len(names)

        start = page * page_size
        end = start + page_size

        chunk = names[start:end]

        await self.send(text_data=json.dumps({
            "type": "participants_page",
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": max(1, -(-total // page_size)),
            "usernames": chunk,
        }))

    # =====================================================
    # QUIZ FLOW
    # =====================================================
    async def _start_quiz(self):

        rs = runtime_sessions.get(self.session_code)

        if rs:
            rs["active"] = True
            rs["status"] = "waiting"
            rs["current_q"] = None
            rs["counts"] = {}
            rs["question_start"] = None
        await self._set_session_state("waiting", clear_question=True)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "quiz_started"
                }
            }
        )
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "host_update",
                    "status": "quiz_started",
                }
            }
        )

    async def _end_quiz(self):

        rs = runtime_sessions.get(self.session_code)

        if not rs:
            return

        rs["active"] = False
        rs["status"] = "ended"
        await self._set_session_state("ended", clear_question=True)

        counts = rs["counts"]
        current_q = rs["current_q"]

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "question_ended",
                    "counts": counts
                }
            }
        )
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "host_update",
                    "status": "quiz_ended",
                }
            }
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "quiz_ended",
                    "question": current_q,
                    "counts": counts
                }
            }
        )

        rs["current_q"] = None
        rs["counts"] = {}
        rs["question_start"] = None

    async def _end_session(self):
        rs = runtime_sessions.get(self.session_code)
        if rs:
            rs["active"] = False
            rs["status"] = "ended"
            rs["current_q"] = None
            rs["counts"] = {}
            rs["question_start"] = None
        await self._set_session_state("ended", clear_question=True)
        try:
            r = _get_redis()
            await r.hset(f"quiz:{self.session_code}:state", mapping={"status": "ended", "active": "0", "current_q": ""})
        except Exception:
            pass

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "session_ended"
                }
            }
        )
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "host_update",
                    "status": "session_ended",
                }
            }
        )

    async def _next_question(self):
        rs = runtime_sessions.get(self.session_code)
        if rs:
            rs["status"] = "waiting"
            rs["current_q"] = None
            rs["counts"] = {}
            rs["question_start"] = None
        await self._set_session_state("waiting", clear_question=True)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "next_question"
                }
            }
        )
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "host_update",
                    "status": "next_question",
                }
            }
        )

    # =====================================================
    # AUTO CLOSE
    # =====================================================
    async def _close_question_after(self, session_code, secs):

        try:

            await asyncio.sleep(secs)

            rs = runtime_sessions.get(session_code)

            if not rs:
                return

            try:
                r = _get_redis()
                counts_key = f"quiz:{session_code}:counts"
                raw_counts = await r.hgetall(counts_key)
                if raw_counts:
                    counts = {k: int(v) for k, v in raw_counts.items()}
                    rs["counts"] = counts
                else:
                    counts = dict(rs.get("counts", {}))
                await r.hset(f"quiz:{session_code}:state", "status", "closed")
            except Exception:
                counts = dict(rs.get("counts", {}))

            await self.channel_layer.group_send(
                f"quiz_{session_code}",
                {
                    "type": "send_json",
                    "payload": {
                        "type": "question_closed",
                        "counts": counts
                    }
                }
            )

            rs["last_q"] = rs.get("current_q")
            rs["last_counts"] = counts
            rs["current_q"] = rs.get("current_q")
            rs["counts"] = counts
            rs["question_start"] = None
            rs["status"] = "closed"
            current_q = rs.get("current_q")
            await self._set_session_state("closed", question_id=current_q.get("id") if current_q else None)

        except asyncio.CancelledError:
            return

    def _shuffle_question_choices(self, question):
        q = dict(question)
        choices = [dict(choice) for choice in q.get("choices", [])]
        random.shuffle(choices)
        q["choices"] = choices
        return q

    async def _send_current_state(self, username=None):
        await self._send_sync_state(username, legacy=True)

    async def _send_sync_state(self, username=None, legacy=False):
        await self._hydrate_runtime_from_db()
        rs = runtime_sessions.get(self.session_code)
        if not rs:
            return

        # Hydrate from Redis shared state if available
        try:
            r = _get_redis()
            st = await r.hgetall(f"quiz:{self.session_code}:state")
            if st:
                rs["status"] = st.get("status", rs.get("status", "waiting"))
                if "question_json" in st:
                    rs["current_q"] = json.loads(st["question_json"])
                if "expires_in" in st:
                    rs["duration"] = int(st["expires_in"])
                if "question_start" in st and st["question_start"]:
                    rs["question_start"] = int(st["question_start"])
            raw_counts = await r.hgetall(f"quiz:{self.session_code}:counts")
            if raw_counts:
                rs["counts"] = {k: int(v) for k, v in raw_counts.items()}
        except Exception:
            pass

        status_val = rs.get("status", "waiting")
        counts_val = rs.get("counts") or rs.get("last_counts") or {}

        payload = {
            "type": "current_state" if legacy else "sync_state",
            "state": status_val,
            "status": status_val,
            "counts": counts_val,
            "question_index": rs.get("question_index", 0),
            "current_question_index": rs.get("question_index", 0),
            "session_active": rs.get("active", False),
        }

        current_q = rs.get("current_q")
        if current_q:
            elapsed_sec = 0
            if rs.get("question_start"):
                elapsed_sec = (int(time.time() * 1000) - rs["question_start"]) / 1000
            remaining = max(1, int(rs.get("duration", 20) - elapsed_sec))

            # Security: unrevealed questions sent to players must NOT leak is_correct
            safe_q = current_q if (self.is_host or status_val in ("answer_reveal", "leaderboard", "closed")) else _sanitize_question_for_player(current_q)

            payload.update({
                "status": status_val if status_val != "waiting" else "question",
                "question": safe_q,
                "expires_in": remaining,
                "duration": rs.get("duration", 20),
                "timer_remaining": remaining,
                "answered": await self._has_answered(username, current_q.get("id")),
            })

        await self.send(text_data=json.dumps(payload))

    # =====================================================
    # GRAPH UPDATE
    # =====================================================
    def _schedule_graph_update(self, rs):

        task = rs.get("_graph_task")

        if task and not task.done():
            return

        rs["_graph_task"] = asyncio.create_task(
            self._debounced_graph_update(rs)
        )

    async def _debounced_graph_update(self, rs):

        await asyncio.sleep(GRAPH_DEBOUNCE_SEC)

        try:
            r = _get_redis()
            counts_key = f"quiz:{self.session_code}:counts"
            raw_counts = await r.hgetall(counts_key)
            if raw_counts:
                counts = {k: int(v) for k, v in raw_counts.items()}
                rs["counts"] = counts
            else:
                counts = dict(rs.get("counts", {}))
        except Exception:
            counts = dict(rs.get("counts", {}))

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "graph_update",
                    "counts": counts
                }
            }
        )

        rs["_graph_task"] = None

    # =====================================================
    # AVATAR UPDATE
    # =====================================================
    async def _handle_avatar_update(self, data):
        username  = (data.get("username") or "").strip()
        avatar_id = int(data.get("avatar_id") or 0)

        if not username:
            return

        # Persist to DB
        await self._update_avatar_db(username, avatar_id)

        # Broadcast to all clients so every player sees the change
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "avatar_update",
                    "username": username,
                    "avatar_id": avatar_id,
                }
            }
        )
        rs = runtime_sessions.get(self.session_code)
        if rs:
            self._schedule_lobby_update(rs)

    # =====================================================
    # PROFILE IMAGE UPDATE
    # =====================================================
    async def _handle_profile_image_update(self, data):
        username = (data.get("username") or "").strip()
        image_data = data.get("image_data") or ""
        if not username or not image_data:
            return
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "profile_image_update",
                    "username": username,
                    "image_data": image_data,
                }
            }
        )

    # =====================================================
    # AVATAR IMAGE URL (server URL broadcast)
    # =====================================================
    async def _handle_avatar_image_url(self, data):
        username = (data.get("username") or "").strip()
        image_url = (data.get("image_url") or "").strip()
        if not username or not image_url:
            return
        await self._update_avatar_url_db(username, image_url)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "avatar_image_url",
                    "username": username,
                    "image_url": image_url,
                }
            }
        )

    # =====================================================
    # LOBBY UPDATE  (sends full participant objects)
    # =====================================================
    def _schedule_lobby_update(self, rs):

        task = rs.get("_lobby_task")

        if task and not task.done():
            return

        rs["_lobby_task"] = asyncio.create_task(
            self._debounced_lobby_update(rs)
        )

    async def _debounced_lobby_update(self, rs):

        await asyncio.sleep(LOBBY_BATCH_SEC)

        # Fetch full participant data from DB so avatar_ids are included
        participants = await self._get_participants_with_avatars()

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_json",
                "payload": {
                    "type": "lobby_update",
                    "participants": participants,
                    "count": len(participants)
                }
            }
        )

        rs["_lobby_task"] = None

    # =====================================================
    # SEND JSON
    # =====================================================
    async def send_json(self, event):

        payload = event.get("payload")

        if payload:
            ptype = payload.get("type")
            rs = runtime_sessions.get(self.session_code)
            if rs:
                if ptype == "question":
                    rs["status"] = "question"
                    rs["current_q"] = payload.get("question")
                    rs["duration"] = payload.get("duration", 20)
                elif ptype == "correct_revealed":
                    rs["status"] = "answer_reveal"
                    if "counts" in payload:
                        rs["counts"] = payload["counts"]
                elif ptype == "question_closed":
                    rs["status"] = "closed"
                    if "counts" in payload:
                        rs["counts"] = payload["counts"]
                elif ptype in ("quiz_ended", "session_ended"):
                    rs["status"] = "ended"
                    rs["active"] = False

            await self.send(
                text_data=json.dumps(payload)
            )

    # =====================================================
    # DATABASE HELPERS
    # =====================================================
    @sync_to_async
    def _set_session_state(self, state, question_id=None, question_index=None, duration=None, clear_question=False):
        try:
            session = QuizSession.objects.select_related("current_quiz_set").get(code=self.session_code)
            session.state = state
            session.session_active = state != "ended"
            session.started = False if state == "ended" else (state != "waiting" or session.started)
            session.finished = state == "ended"

            if clear_question:
                session.current_question = None
                session.timer_duration_seconds = 0
                session.state_started_at = None
            elif question_id:
                question = Question.objects.select_related("quiz").get(id=question_id)
                session.current_question = question
                session.current_quiz_set = question.quiz
                if question_index is None:
                    ids = list(
                        question.quiz.questions.order_by("order", "id").values_list("id", flat=True)
                    )
                    question_index = ids.index(question.id) if question.id in ids else session.current_question_index
                session.current_question_index = int(question_index)
                if duration is not None:
                    session.timer_duration_seconds = int(duration)
                if state == "question":
                    session.state_started_at = timezone.now()
            elif state in ("answer_reveal", "leaderboard", "closed"):
                session.state_started_at = None

            session.save(update_fields=[
                "state",
                "session_active",
                "started",
                "finished",
                "current_question",
                "current_quiz_set",
                "current_question_index",
                "timer_duration_seconds",
                "state_started_at",
            ])
        except Exception as exc:
            print("[set_session_state] error:", exc)

    @sync_to_async
    def _hydrate_runtime_from_db(self):
        try:
            session = QuizSession.objects.select_related(
                "current_question", "current_quiz_set"
            ).prefetch_related("current_question__choices", "participants").get(code=self.session_code)
        except QuizSession.DoesNotExist:
            return

        rs = _init_session(self.session_code)
        current_q = _question_payload(session.current_question)
        rs["status"] = session.state or "waiting"
        rs["active"] = bool(session.session_active)
        rs["current_q"] = current_q if session.state in ("question", "answer_reveal", "leaderboard", "closed") else None
        if current_q:
            rs["last_q"] = current_q
        rs["duration"] = int(session.timer_duration_seconds or (current_q or {}).get("timer_seconds") or 20)
        rs["question_index"] = int(session.current_question_index or 0)

        if session.state == "question" and session.state_started_at:
            rs["question_start"] = int(session.state_started_at.timestamp() * 1000)
        elif session.state != "question":
            rs["question_start"] = None

        db_usernames = [
            participant.username
            for participant in session.participants.all().order_by("joined_at", "id")
        ]
        if db_usernames:
            rs["usernames"] = db_usernames

    @sync_to_async
    def _validate_participant(self, username):
        try:
            session = QuizSession.objects.get(code=self.session_code)
            # If session hasn't started yet, allow anyone who has a DB participant record
            # (created by the HTTP join endpoint). If no record exists yet due to a race
            # condition, allow them through — the HTTP join already validated them.
            if not session.started:
                return True
            return Participant.objects.filter(
                session=session,
                username=username
            ).exists()
        except QuizSession.DoesNotExist:
            return False

    @sync_to_async
    def _update_avatar_db(self, username, avatar_id):
        try:
            session = QuizSession.objects.get(code=self.session_code)
            Participant.objects.filter(
                session=session, username=username
            ).update(avatar_id=avatar_id)
        except QuizSession.DoesNotExist:
            pass
    @sync_to_async 
    def _update_avatar_url_db(self, username, image_url):  # ← add here
        try:
           session = QuizSession.objects.get(code=self.session_code)
           Participant.objects.filter(
               session=session, username=username
           ).update(avatar_url=image_url)
        except QuizSession.DoesNotExist:
            pass
    
    @sync_to_async
    def _get_participants_with_avatars(self):
        try:
            session = QuizSession.objects.get(code=self.session_code)
            return [
                {"username": p.username, "avatar_id": p.avatar_id or 0, "avatar_url": p.avatar_url or "",}
                for p in Participant.objects.filter(session=session)
            ]
        except QuizSession.DoesNotExist:
            return []

    @sync_to_async
    def _create_participant_db(self, username, avatar_id):

        try:

            session = QuizSession.objects.get(
                code=self.session_code
            )

            participant, created = Participant.objects.get_or_create(
                session=session,
                username=username,
                defaults={
                    "avatar_id": avatar_id,
                    "score": 0
                },
            )
            if not created and participant.avatar_id != avatar_id:
                participant.avatar_id = avatar_id
                participant.save(update_fields=["avatar_id"])

        except QuizSession.DoesNotExist:
            pass

    @sync_to_async
    def _verify_host_token(self, token_key):
        if not token_key:
            return False
        try:
            from rest_framework.authtoken.models import Token
            from quiz.models import QuizSession
            token_str = str(token_key).strip()
            if token_str.startswith("Token "):
                token_str = token_str[6:].strip()
            token_obj = Token.objects.select_related('user').get(key=token_str)
            session = QuizSession.objects.select_related('host').get(code=self.session_code)
            user = token_obj.user
            return session.host == user or user.is_staff or user.is_superuser
        except Exception:
            return False

    @sync_to_async
    def _has_answered(self, username, question_id):
        if not username or not question_id:
            return False
        try:
            session = QuizSession.objects.get(code=self.session_code)
            participant = Participant.objects.get(session=session, username=username)
            return AnswerRecord.objects.filter(
                participant=participant,
                question_id=question_id
            ).exists()
        except Exception:
            return False

    @sync_to_async
    def _remove_participant_db(self, username):

        try:

            session = QuizSession.objects.get(
                code=self.session_code
            )

            Participant.objects.filter(
                session=session,
                username=username
            ).delete()

        except QuizSession.DoesNotExist:
            pass

    # =====================================================
    # ANSWER SAVE
    # =====================================================
    async def _persist_answer_task(
        self,
        username,
        selected_choice_id,
        rt,
        question
    ):

        score_payload = await self._persist_answer(
            username,
            selected_choice_id,
            rt,
            question
        )
        if score_payload:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send_json",
                    "payload": {
                        "type": "score_update",
                        **score_payload,
                    }
                }
            )

    @sync_to_async
    def _persist_answer(
        self,
        username,
        selected_choice_id,
        rt,
        question
    ):
        try:
            if not question or not selected_choice_id:
                return None

            try:
                c_id = int(selected_choice_id)
            except (ValueError, TypeError):
                c_id = None

            q_id = question.get("id") if isinstance(question, dict) else getattr(question, "id", None)
            if q_id is None:
                return None

            choice_obj = None
            if c_id is not None:
                choice_obj = Choice.objects.filter(id=c_id, question_id=q_id).first()
                if choice_obj is None:
                    choice_obj = Choice.objects.filter(id=c_id).first()
            else:
                # Text-based choice lookup fallback
                raw_str = str(selected_choice_id).strip()
                choice_obj = Choice.objects.filter(question_id=q_id, text__iexact=raw_str).first()
                if choice_obj:
                    c_id = choice_obj.id

            if choice_obj is not None:
                is_correct = bool(choice_obj.is_correct)
            else:
                # Fallback to in-memory check if Choice lookup fails
                is_correct = False
                for c in (question.get("choices") or []):
                    c_str_id = str(c.get("id"))
                    c_str_text = str(c.get("text") or "").strip().lower()
                    sel_str = str(selected_choice_id).strip().lower()
                    if c_str_id == str(selected_choice_id) or (sel_str and c_str_text == sel_str):
                        is_correct = bool(c.get("is_correct"))
                        try:
                            c_id = int(c.get("id"))
                        except Exception:
                            pass
                        break

            if c_id is None:
                return None

            participant = Participant.objects.filter(
                session__code=self.session_code,
                username=username
            ).first()

            if not participant:
                return None

            from django.db import transaction
            with transaction.atomic():
                # Concurrency double check inside transaction to prevent duplicate AnswerRecord (BUG-02)
                if AnswerRecord.objects.filter(participant=participant, question_id=q_id).exists():
                    return None

                record = AnswerRecord.objects.create(
                    participant=participant,
                    question_id=q_id,
                    choice_id=c_id,
                    correct=is_correct,
                    response_time_ms=rt,
                )

            # SCORE
            if is_correct:
                max_score = 1000
                timer_sec = question.get("timer_seconds", 30) or 30
                time_fraction = min(rt / (timer_sec * 1000), 1.0)
                score = max(100, int(max_score * (1 - 0.5 * time_fraction)))

                participant.score = (participant.score or 0) + score
                participant.total_response_time = (participant.total_response_time or 0) + rt
                participant.save(update_fields=["score", "total_response_time"])

            attended = AnswerRecord.objects.filter(participant=participant).count()
            correct = AnswerRecord.objects.filter(participant=participant, correct=True).count()
            accuracy = round((correct / attended) * 100) if attended > 0 else 0

            # Invalidate cache so polling responses are immediately updated
            try:
                from .views import invalidate_participants_cache
                invalidate_participants_cache(self.session_code)
            except Exception:
                pass

            return {
                "username": participant.username,
                "score": participant.score or 0,
                "avatar_id": participant.avatar_id or 0,
                "total_attended": attended,
                "correct_count": correct,
                "accuracy": accuracy,
            }

        except Exception as e:
            print("[persist_answer] error:", e)
        return None
