# QUIZ MASTER — BUG TRACKER & DEFECT LOG

**Audit Date:** November 17, 2026  
**Auditor:** Senior QA Automation & Software Architecture Team  
**Scope:** Frontend (React), Backend (Django REST Framework), Real-time (Django Channels / Daphne / Redis), Database (SQLite)

---

## 1. Summary of Identified Defects

| Bug ID | Severity | Priority | Title | Affected Component | File Path |
|---|---|---|---|---|---|
| **BUG-01** | **Critical** | **P0** | Unauthenticated WebSocket Host Role Hijacking | Django Channels Consumer | `backend/quiz/consumers.py:289-305` |
| **BUG-02** | **Critical** | **P0** | Duplicate `AnswerRecord` Database Entries on Concurrency Race | Django ORM / SQLite Schema | `backend/quiz/models.py:106-112` |
| **BUG-03** | **High** | **P1** | Cross-Site WebSocket Hijacking (CSWSH) via Wildcard Origin | Django Settings / AllowedHosts | `backend/backend/settings.py:53-56` |
| **BUG-04** | **High** | **P1** | Player Impersonation in WebSocket Answer Submissions | Django Channels Consumer | `backend/quiz/consumers.py:483-525` |
| **BUG-05** | **High** | **P1** | Live Vote Count Inflation via Unvalidated Redis `HINCRBY` | Redis Live Count Layer | `backend/quiz/consumers.py:516-523` |
| **BUG-06** | **High** | **P1** | High Concurrency Database Lock Timeouts (>50 users) | Database Engine Configuration | `backend/backend/settings.py:126-135` |
| **BUG-07** | **Medium** | **P2** | Unsanitized Player Username Allows Stored HTML / Script Injection | Join API & Participant Model | `backend/quiz/views.py:328-354` |
| **BUG-08** | **Medium** | **P2** | Quiz Set Creation API Fails on Empty Questions Array | REST API Serializer | `backend/quiz/serializers.py:12-25` |
| **BUG-09** | **Medium** | **P2** | In-Memory `runtime_sessions` Dict Breaks Multi-Worker Scale | Real-Time Session Store | `backend/quiz/consumers.py:52-92` |
| **BUG-10** | **Low** | **P3** | Duplicate Style Keys and ESLint Syntax Warnings in Frontend | React Frontend Components | `frontend/src/pages/Lobby.js`, `AudienceDisplay.js` |

---

## 2. Detailed Defect Reports

### BUG-01: Unauthenticated WebSocket Host Role Hijacking
- **Bug ID**: `BUG-01`
- **Severity**: Critical | **Priority**: P0
- **Affected Module**: Real-Time Consumer (`QuizConsumer`)
- **Source File**: [`backend/quiz/consumers.py:289-305`](file:///C:/A2757/QuizProject/backend/quiz/consumers.py#L289-L305)
- **Steps to Reproduce**:
  1. Establish a WebSocket connection to `ws://127.0.0.1:8001/ws/quiz/<active_pin>/`.
  2. Send `{ "action": "join", "username": "Attacker", "role": "host" }` without providing any auth token.
  3. Server acknowledges with `{ "type": "joined", "username": "Attacker", "role": "host" }`.
  4. Send `{ "action": "start_quiz" }` or `{ "action": "end_session" }`.
- **Expected Behavior**: Connection must be rejected or restricted unless a valid Django REST Token matching the session's actual host (`QuizSession.host`) is provided and verified.
- **Actual Behavior**: The consumer accepts `is_host = True` for any connection that specifies `role: "host"`, overwriting `rs["host_channel"]` and granting full quiz master privileges to an anonymous spectator.
- **Root Cause**:
  ```python
  role = data.get("role", "participant")
  is_host = role == "host"
  is_valid = True if is_host else await self._validate_participant(username)
  ```
- **Proposed Solution**: Require an authentication token in the `join` payload for `role: "host"` and validate `Token.objects.filter(key=token, user=session.host).exists()`.
- **Regression Test**: Run `scratch/qa_suite/qa_test_security_audit.py::SEC-04`.

---

### BUG-02: Duplicate `AnswerRecord` Database Entries on Concurrency Race
- **Bug ID**: `BUG-02`
- **Severity**: Critical | **Priority**: P0
- **Affected Module**: Database Models & Answer Persistence
- **Source File**: [`backend/quiz/models.py:106-112`](file:///C:/A2757/QuizProject/backend/quiz/models.py#L106-L112) & [`backend/quiz/consumers.py:1435-1448`](file:///C:/A2757/QuizProject/backend/quiz/consumers.py#L1435-L1448)
- **Steps to Reproduce**:
  1. Two rapid answer submissions for the same participant and question arrive concurrently.
  2. Both threads evaluate `AnswerRecord.objects.get_or_create(...)` simultaneously before the first transaction commits.
  3. Both write distinct rows into `quiz_answerrecord`.
- **Expected Behavior**: Database enforces integrity with `unique_together = ['participant', 'question']` or a `UniqueConstraint`.
- **Actual Behavior**: Found 20+ historical duplicate records in the database (e.g. Participant 23 Question 4 has 9 duplicate answer records).
- **Root Cause**: The `AnswerRecord` model lacks a unique database constraint on `('participant', 'question')`.
- **Proposed Solution**:
  1. Add a deduplication migration to clean historical duplicate records.
  2. Add `class Meta: unique_together = ['participant', 'question']` to `AnswerRecord`.
- **Regression Test**: Run `scratch/qa_suite/qa_test_database.py::DB-01` and `DB-02`.

---

### BUG-03: Cross-Site WebSocket Hijacking (CSWSH) via Wildcard Origin
- **Bug ID**: `BUG-03`
- **Severity**: High | **Priority**: P1
- **Affected Module**: Django Settings / Channels Origin Security
- **Source File**: [`backend/backend/settings.py:53-56`](file:///C:/A2757/QuizProject/backend/backend/settings.py#L53-L56)
- **Steps to Reproduce**:
  1. Connect to `ws://127.0.0.1:8001/ws/quiz/<pin>/` with `Origin: http://evil-attacker-site.com`.
  2. Handshake succeeds with HTTP 101 Switching Protocols.
- **Expected Behavior**: AllowedHostsOriginValidator should reject origins not present in `FRONTEND_ORIGINS`.
- **Actual Behavior**: Handshake is accepted because `'*'` is present in `ALLOWED_HOSTS` when `DEBUG=True`.
- **Root Cause**: `ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,*')`.
- **Proposed Solution**: Remove `'*'` from `ALLOWED_HOSTS` and configure explicit trusted frontend origins in `AllowedHostsOriginValidator` / settings.
- **Regression Test**: Run `scratch/qa_suite/qa_test_websockets.py::WS-02`.

---

### BUG-04: Player Impersonation in WebSocket Answer Submissions
- **Bug ID**: `BUG-04`
- **Severity**: High | **Priority**: P1
- **Affected Module**: Real-Time Answer Dispatcher
- **Source File**: [`backend/quiz/consumers.py:483-490`](file:///C:/A2757/QuizProject/backend/quiz/consumers.py#L483-L490)
- **Steps to Reproduce**:
  1. Player A connects and authenticates as "Attacker".
  2. Player A sends `{ "action": "answer", "username": "Victim", "choice_id": 101 }`.
  3. Server records the answer under "Victim".
- **Expected Behavior**: The server must verify that the answer comes from the authenticated username bound to that specific WebSocket session (`self.username`).
- **Actual Behavior**: The server blindly trusts `data.get("username")` from the incoming message payload.
- **Root Cause**:
  ```python
  username = data.get("username", "") # ignores self.username
  ```
- **Proposed Solution**: Enforce `username = self.username` and ignore any unverified client-provided username.
- **Regression Test**: Run `scratch/qa_suite/qa_test_security_audit.py::SEC-05`.

---

### BUG-05: Live Vote Count Inflation via Unvalidated Redis `HINCRBY`
- **Bug ID**: `BUG-05`
- **Severity**: High | **Priority**: P1
- **Affected Module**: Real-Time Vote Aggregation
- **Source File**: [`backend/quiz/consumers.py:516-523`](file:///C:/A2757/QuizProject/backend/quiz/consumers.py#L516-L523)
- **Steps to Reproduce**:
  1. A connected player script rapidly fires 50 `action: "answer"` messages during an active question.
  2. Redis increments the choice count 50 times.
  3. The audience and host graph updates display 50 votes cast by a single participant.
- **Expected Behavior**: Redis counts should only increment once per participant per question.
- **Actual Behavior**: `r.hincrby(counts_key, choice_key_str, 1)` executes unconditionally on every message receipt before verifying prior submission.
- **Root Cause**: Redis does not maintain an atomic set of participants who have already voted for the active question.
- **Proposed Solution**: Use a Redis Set `quiz:<pin>:voted:<q_id>` with `SADD`. Only if `SADD` returns 1 (new voter) do we execute `HINCRBY`.
- **Regression Test**: Run `scratch/qa_suite/qa_test_security_audit.py::SEC-06`.

---

### BUG-06: High Concurrency Database Lock Timeouts (>50 users)
- **Bug ID**: `BUG-06`
- **Severity**: High | **Priority**: P1
- **Affected Module**: Database Concurrency & Storage Engine
- **Source File**: [`backend/backend/settings.py:126-135`](file:///C:/A2757/QuizProject/backend/backend/settings.py#L126-L135)
- **Steps to Reproduce**:
  1. Execute load test with 100 concurrent users joining simultaneously.
  2. Latency climbs to 4,267ms; 12% error rate occurs.
  3. At 250 concurrent users, 64% error rate occurs with `sqlite3.OperationalError: database is locked`.
- **Expected Behavior**: Database handles concurrent writes with row-level locking.
- **Actual Behavior**: SQLite default file-locking blocks concurrent writes from asynchronous Daphne worker coroutines.
- **Root Cause**: SQLite is designed for single-writer workloads; concurrent participant creation and answer recording exhaust the default 5-second lock timeout.
- **Proposed Solution**: Configure PostgreSQL (or enable SQLite WAL mode with 30s timeout as an interim dev mitigation).
- **Regression Test**: Run `scratch/qa_suite/qa_test_load.py`.

---

### BUG-07: Unsanitized Player Username Allows Stored HTML / Script Injection
- **Bug ID**: `BUG-07`
- **Severity**: Medium | **Priority**: P2
- **Affected Module**: Participant Join & Display
- **Source File**: [`backend/quiz/views.py:328-354`](file:///C:/A2757/QuizProject/backend/quiz/views.py#L328-L354)
- **Steps to Reproduce**:
  1. Call `POST /api/join/<pin>/` with `{"username": "<script>alert('xss')</script>"}`.
  2. The server saves the raw HTML string into the database and broadcasts it over WebSocket and REST APIs.
- **Expected Behavior**: Usernames must be sanitized (stripped of HTML/special characters, alphanumeric + basic punctuation, max length 24).
- **Actual Behavior**: Raw script tags are persisted and returned in JSON payloads.
- **Root Cause**: `username = str(username).strip()` lacks character whitelisting or escaping.
- **Proposed Solution**: Add regex validation `^[a-zA-Z0-9 _-]{2,24}$` in `join_session`.
- **Regression Test**: Run `scratch/qa_suite/qa_test_security_audit.py::SEC-08`.

---

### BUG-08: Quiz Set Creation API Fails on Empty Questions Array
- **Bug ID**: `BUG-08`
- **Severity**: Medium | **Priority**: P2
- **Affected Module**: Quiz Set Serializer
- **Source File**: [`backend/quiz/serializers.py:12-25`](file:///C:/A2757/QuizProject/backend/quiz/serializers.py#L12-L25)
- **Steps to Reproduce**:
  1. Call `POST /api/quizsets/` with `{"title": "My New Quiz", "questions": []}`.
  2. API rejects request with HTTP 400: `{"questions": ["This field is required."]}`.
- **Expected Behavior**: Allow creating a draft quiz title first, then appending questions later.
- **Actual Behavior**: Serializer requires `questions` with choices during initial quiz set creation.
- **Root Cause**: `questions = QuestionSerializer(many=True)` without `required=False`.
- **Proposed Solution**: Set `required=False, default=list` on `questions` in `QuizSetSerializer`.
- **Regression Test**: Run `scratch/qa_suite/qa_test_auth_and_api.py::QUIZ-01`.

---

### BUG-09: In-Memory `runtime_sessions` Dict Breaks Multi-Worker Scale
- **Bug ID**: `BUG-09`
- **Severity**: Medium | **Priority**: P2
- **Affected Module**: Real-Time State Management
- **Source File**: [`backend/quiz/consumers.py:52-92`](file:///C:/A2757/QuizProject/backend/quiz/consumers.py#L52-L92)
- **Steps to Reproduce**:
  1. Launch Daphne with 2 worker processes: `daphne -u 2 ...`.
  2. Host connects to Worker 1; Player connects to Worker 2.
  3. Worker 2 does not share Worker 1's `runtime_sessions` in-memory dictionary.
- **Expected Behavior**: Session state, active question, and timers are managed centrally in Redis.
- **Actual Behavior**: Server partially uses Redis for counts, but relies on process-local `runtime_sessions` for `close_task` timers and local question caching.
- **Root Cause**: Hybrid architectural design: local in-memory dictionary combined with ad-hoc Redis calls.
- **Proposed Solution**: Fully persist active session state (`status`, `question_id`, `expires_at`) in Redis hashes so any worker can process any message statelessly.

---

### BUG-10: Duplicate Style Keys and ESLint Syntax Warnings in Frontend
- **Bug ID**: `BUG-10`
- **Severity**: Low | **Priority**: P3
- **Affected Module**: React UI Components
- **Source File**: `frontend/src/pages/AlreadyJoined.js`, `AudienceDisplay.js`, `AudienceJoin.js`
- **Steps to Reproduce**: Run `npm run build`.
- **Expected Behavior**: Clean build with zero duplicate keys or warnings.
- **Actual Behavior**: 15+ warnings for duplicate style keys (`fontWeight`, `border`, `color`).
- **Proposed Solution**: Clean up inline CSS style objects.
