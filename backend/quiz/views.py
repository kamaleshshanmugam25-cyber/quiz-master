
import time
from django.db.models import Count, Q

_participants_cache = {}  # code -> (timestamp, data)
PARTICIPANTS_CACHE_TTL = 0.75  # 750ms in-memory cache to absorb polling storms

def invalidate_participants_cache(code=None):
    if code:
        _participants_cache.pop(code, None)
    else:
        _participants_cache.clear()
import logging
import traceback
import random
import string
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .consumers import runtime_sessions, _init_session
from .models import QuizSet, QuizSession, SessionQuizSet, Participant, Question, Choice
from .serializers import (
    QuizSetSerializer, QuizSessionSerializer, SessionQuizSetSerializer,
    ParticipantSerializer, QuestionSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


def _participant_payload(participant):
    return {
        "id": participant.id,
        "username": participant.username,
        "score": participant.score or 0,
        "total_response_time": participant.total_response_time or 0,
        "avatar_id": participant.avatar_id or 0,
        "avatar_url": participant.avatar_url or None,
    }


def _session_participants_payload(session):
    return [
        _participant_payload(participant)
        for participant in session.participants.all().order_by('joined_at', 'id')
    ]


# ----------------- Utility: Parse extracted PDF text into questions -----------------
def _parse_text_to_questions(raw_text: str):
    lines = [l.strip() for l in raw_text.splitlines()]
    question_pattern = re.compile(r"^\s*Q?(\d{1,3})[\.\)]\s+(.*)", re.IGNORECASE)
    option_pattern = re.compile(r"^\s*([A-Da-d])[\.\)]\s+(.*)")
    answer_pattern = re.compile(r"^\s*Answer:\s*([A-Da-d])\s*$", re.IGNORECASE)

    questions = []
    current = None
    correct_answer = None

    for line in lines:
        if not line:
            continue

        answer_match = answer_pattern.match(line)
        if answer_match and current is not None:
            correct_answer = answer_match.group(1).upper()
            for choice in current.get("choices", []):
                if choice.get("letter") == correct_answer:
                    choice["is_correct"] = True
            continue

        qmatch = question_pattern.match(line)
        if qmatch:
            if current is not None and current.get("text") and len(current.get("choices", [])) >= 2:
                questions.append(current)
            current = {
                "text": qmatch.group(2).strip(),
                "timer_seconds": 20,
                "image": None,
                "choices": []
            }
            correct_answer = None
            continue

        omatch = option_pattern.match(line)
        if omatch and current is not None:
            opt_text = omatch.group(2).strip()
            choice_letter = omatch.group(1).upper()
            current["choices"].append({
                "text": opt_text,
                "is_correct": False,
                "letter": choice_letter
            })
            continue

        if current is not None and not option_pattern.match(line) and not answer_pattern.match(line):
            if current.get("text"):
                current["text"] += " " + line
            else:
                current["text"] = line

    if current is not None and current.get("text") and len(current.get("choices", [])) >= 2:
        questions.append(current)

    return questions


# ----------------- Utility: Guess a quiz title from extracted text -----------------
def _guess_title_from_text(raw_text: str) -> str:
    try:
        lines = [l.strip() for l in raw_text.splitlines()]
        question_pattern = re.compile(r"^\s*(Q?\d{1,3}[\).])\s+", re.IGNORECASE)
        option_pattern = re.compile(r"^\s*[A-Da-d][\).]\s+")
        answer_pattern = re.compile(r"^\s*Answer:\s*[A-Da-d]\s*$", re.IGNORECASE)
        for line in lines:
            if not line:
                continue
            if question_pattern.match(line):
                continue
            if option_pattern.match(line):
                continue
            if answer_pattern.match(line):
                continue
            return line[:120]
    except Exception:
        pass
    return ""


class QuizSetViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return QuizSet.objects.filter(
            created_by=self.request.user, session_only=False
        ).prefetch_related('questions__choices')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quizsets(request):
    if request.method == 'GET':
        quizzes = QuizSet.objects.filter(
            created_by=request.user, session_only=False
        ).prefetch_related('questions__choices')
        serializer = QuizSetSerializer(quizzes, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = QuizSetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def quizset_detail(request, quizset_id):
    try:
        quizset = QuizSet.objects.prefetch_related(
            'questions__choices'
        ).get(id=quizset_id, created_by=request.user)
    except QuizSet.DoesNotExist:
        return Response({"error": "Quiz set not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuizSetSerializer(quizset)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = QuizSetSerializer(quizset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        quizset.delete()
        return Response({"message": "Quiz set deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def question_detail(request, quizset_id, question_id):
    try:
        quizset = QuizSet.objects.get(id=quizset_id, created_by=request.user)
        question = quizset.questions.prefetch_related('choices').get(id=question_id)
    except (QuizSet.DoesNotExist, Question.DoesNotExist):
        return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = QuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        question.delete()
        return Response({"message": "Question deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_session(request):
    qs = QuizSession.objects.filter(
        host=request.user, finished=False
    ).only('id', 'code', 'started', 'finished', 'state', 'session_active').first()
    if qs:
        return Response({
            "id": qs.id,
            "code": qs.code,
            "started": qs.started,
            "finished": qs.finished,
            "state": qs.state,
            "session_active": qs.session_active,
        })
    return Response({"active": False})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session(request):
    quiz_set_ids = request.data.get('quiz_set_ids', [])

    if not quiz_set_ids:
        return Response({"error": "At least one quiz set is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Auto-close all stale unfinished sessions for this user (browser closed, server restarted, etc.)
    QuizSession.objects.filter(
        host=request.user,
        finished=False
    ).update(finished=True, session_active=False, state='ended')

    while True:
        code = ''.join(random.choices(string.digits, k=6))
        if not QuizSession.objects.filter(code=code).exists():
            break

    session = QuizSession.objects.create(code=code, host=request.user, started=False, finished=False)

    owned_quizsets = list(QuizSet.objects.filter(id__in=quiz_set_ids, created_by=request.user))
    if len(owned_quizsets) != len(quiz_set_ids):
        return Response({"error": "You can only start sessions with your own quiz sets."}, status=status.HTTP_403_FORBIDDEN)

    quizset_map = {q.id: q for q in owned_quizsets}
    for i, quiz_set_id in enumerate(quiz_set_ids):
        quiz_set = quizset_map.get(quiz_set_id)
        if quiz_set is None:
            continue
        SessionQuizSet.objects.create(session=session, quiz_set=quiz_set, order=i)

    return Response({"code": session.code, "session_id": session.id})


@api_view(['GET'])
@permission_classes([AllowAny])
def session_quiz(request, code):
    session = get_object_or_404(
        QuizSession.objects.prefetch_related(
            'quiz_sets__quiz_set__questions__choices'
        ),
        code=code
    )
    try:
        request.session['active_game_pin'] = code
        request.session.modified = True
    except Exception:
        pass
    serializer = QuizSessionSerializer(session)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_pin(request, code):
    exists = QuizSession.objects.filter(code=code, finished=False).exists()
    if exists:
        return Response({"valid": True})
    try:
        request.session['active_game_pin'] = code
        request.session.modified = True
    except Exception:
        pass
    return Response({"valid": False}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def join_session(request, code):
    print(f"Join session called with code: {code}")
    print(f"Request data: {request.data}")

    username = request.data.get('username')
    avatar_id = request.data.get('avatar_id', 0)
    if not username:
        return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

    code = code.strip().upper()
    username = str(username).strip()
    print(f"Cleaned code: {code}, username: {username}")

    try:
        # If session has concluded, inform the user
        finished_session = QuizSession.objects.filter(code=code, finished=True).first()
        if finished_session:
            return Response({"error": "This quiz session has already concluded."}, status=status.HTTP_410_GONE)

        session = QuizSession.objects.get(code=code, finished=False)
        print(f"Found session: {session}, started={session.started}")

        # Check if participant already exists in this session (reconnecting player)
        existing_participant = Participant.objects.filter(session=session, username__iexact=username).first()
        if existing_participant:
            participant = existing_participant
            print(f"Reconnected participant: {participant}")
        else:
            participant = Participant.objects.create(session=session, username=username, avatar_id=avatar_id)
            print(f"Created new participant: {participant}")

        try:
            request.session['active_game_pin'] = session.code
            request.session['player_username'] = username
            request.session.modified = True
        except Exception:
            pass

        try:
            rs = _init_session(session.code)
            if username not in rs["usernames"]:
                rs["usernames"].append(username)
            channel_layer = get_channel_layer()
            payload = {
                "type": "participant_join",
                "participant": _participant_payload(participant),
            }
            async_to_sync(channel_layer.group_send)(f"quiz_{session.code}", {"type": "send_json", "payload": payload})
            payload = {
                "type": "lobby_update",
                "participants": _session_participants_payload(session),
                "count": session.participants.count(),
            }
            async_to_sync(channel_layer.group_send)(f"quiz_{session.code}", {"type": "send_json", "payload": payload})
        except Exception:
            pass

        serializer = ParticipantSerializer(participant)
        res_data = dict(serializer.data)
        res_data['session_id'] = session.code
        res_data['started'] = bool(session.started)
        res_data['finished'] = bool(session.finished)
        res_data['token'] = f"token_{session.code}_{participant.id}"
        return Response(res_data)

    except QuizSession.DoesNotExist:
        print(f"Session not found: {code}")
        return Response({"error": "Invalid session code"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        traceback.print_exc()
        return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_username_availability(request, code, username=None):
    try:
        code = str(code).strip().upper()
        if not username:
            username = request.GET.get('username', '').strip()
        else:
            username = str(username).strip()

        if not username:
            return Response({"available": True, "message": "Username is empty"})

        session = QuizSession.objects.filter(code=code, finished=False).first()
        if not session:
            return Response({"error": "Invalid session code"}, status=status.HTTP_404_NOT_FOUND)

        existing_participant = Participant.objects.filter(
            session=session,
            username__iexact=username
        ).first()
        return Response({
            "available": existing_participant is None,
            "message": "Username is available" if existing_participant is None else "Username is already taken"
        })
    except Exception as e:
        return Response({"available": True, "error": str(e)})

@api_view(['GET'])
@permission_classes([AllowAny])
def session_participants(request, code):
    now = time.time()
    cached = _participants_cache.get(code)
    if cached and (now - cached[0] < PARTICIPANTS_CACHE_TTL):
        return Response(cached[1])

    try:
        session = QuizSession.objects.get(code=code)
        participants = session.participants.annotate(
            annotated_attended=Count('answers'),
            annotated_correct=Count('answers', filter=Q(answers__correct=True))
        ).order_by('-score', 'total_response_time')

        serializer = ParticipantSerializer(participants, many=True)
        data = serializer.data
        _participants_cache[code] = (now, data)
        return Response(data)
    except QuizSession.DoesNotExist:
        return Response({"error": "Invalid session code"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def leave_session(request, code):
    try:
        session = QuizSession.objects.get(code=code, finished=False)
        username = request.data.get('username')

        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        participant = Participant.objects.filter(session=session, username=username).first()
        if participant:
            participant.delete()
            invalidate_participants_cache(code)
            try:
                if code in runtime_sessions:
                    usernames = runtime_sessions[code]["usernames"]
                    if username in usernames:
                        usernames.remove(username)
                channel_layer = get_channel_layer()
                payload = {"type": "participant_leave", "username": username}
                async_to_sync(channel_layer.group_send)(f"quiz_{code}", {"type": "send_json", "payload": payload})
                payload = {
                    "type": "lobby_update",
                    "participants": _session_participants_payload(session),
                    "count": session.participants.count(),
                }
                async_to_sync(channel_layer.group_send)(f"quiz_{code}", {"type": "send_json", "payload": payload})
            except Exception:
                pass
            return Response({"message": "Successfully left session"})
        else:
            return Response({"error": "Participant not found"}, status=status.HTTP_404_NOT_FOUND)

    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz(request, code):
    try:
        session = QuizSession.objects.get(code=code, host=request.user, finished=False)
        if not session.quiz_sets.exists():
            return Response({"error": "No quiz sets added to session"}, status=status.HTTP_400_BAD_REQUEST)

        all_completed = session.quiz_sets.filter(completed=False).count() == 0
        if all_completed:
            session.quiz_sets.update(completed=False)
            session.finished = False

        first_quiz_set = session.quiz_sets.first()
        session.current_quiz_set = first_quiz_set.quiz_set
        session.current_question_index = 0
        session.started = True
        session.save()

        serializer = QuizSessionSerializer(session)
        return Response(serializer.data)
    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_quiz(request, code):
    try:
        session = QuizSession.objects.get(code=code, host=request.user)
        if not session.finished:
            session.started = False
            session.save()
        serializer = QuizSessionSerializer(session)
        return Response(serializer.data)
    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, code):
    try:
        session = QuizSession.objects.get(code=code, host=request.user)
        if not session.finished:
            session.finished = True
            session.session_active = False
            session.state = 'ended'
            session.save(update_fields=['finished', 'session_active', 'state'])
        serializer = QuizSessionSerializer(session)
        return Response(serializer.data)
    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def next_quiz_set(request, code):
    try:
        session = QuizSession.objects.get(code=code, host=request.user, finished=False)

        if session.current_quiz_set:
            current_session_quiz = session.quiz_sets.filter(quiz_set=session.current_quiz_set).first()
            if current_session_quiz:
                current_session_quiz.completed = True
                current_session_quiz.save()

        next_session_quiz = session.quiz_sets.filter(completed=False).first()

        if next_session_quiz:
            session.current_quiz_set = next_session_quiz.quiz_set
            session.current_question_index = 0
            session.save()
            serializer = QuizSessionSerializer(session)
            return Response(serializer.data)
        else:
            session.finished = True
            session.save()
            serializer = QuizSessionSerializer(session)
            return Response({"message": "All quiz sets completed", "session": serializer.data})

    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def next_question(request, code):
    try:
        session = QuizSession.objects.get(code=code, host=request.user, finished=False)

        if not session.current_quiz_set:
            return Response({"error": "No active quiz set"}, status=status.HTTP_400_BAD_REQUEST)

        questions = session.current_quiz_set.questions.prefetch_related(
            'choices'
        ).all().order_by('order')
        total_questions = questions.count()

        if total_questions == 0:
            return Response({"error": "No questions in current quiz set"}, status=status.HTTP_400_BAD_REQUEST)

        if session.current_question_index >= total_questions - 1:
            return Response({"error": "Already at the last question of this quiz set"}, status=status.HTTP_400_BAD_REQUEST)

        session.current_question_index += 1
        session.save()

        next_question = questions[session.current_question_index]

        serializer = QuizSessionSerializer(session)
        return Response({
            "session": serializer.data,
            "next_question": {
                "id": next_question.id,
                "text": next_question.text,
                "timer_seconds": next_question.timer_seconds,
                "order": next_question.order,
                "choices": [
                    {
                        "id": choice.id,
                        "text": choice.text,
                        "is_correct": choice.is_correct
                    } for choice in next_question.choices.all()
                ]
            },
            "question_index": session.current_question_index,
            "total_questions": total_questions
        })

    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_register(request):
    try:
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        username = request.data.get('username', '').strip()
        logger.info(
            "admin_register request received username=%s email=%s",
            username or "<empty>",
            email or "<empty>",
        )

        if not email:
            logger.warning("admin_register validation failed: missing email")
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            logger.warning("admin_register validation failed: missing password for email=%s", email)
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        if '@' not in email or '.' not in email.split('@')[-1]:
            logger.warning("admin_register validation failed: invalid email format email=%s", email)
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
        if not username:
            username = email.split('@')[0]
        if len(username) < 3:
            logger.warning("admin_register validation failed: short username username=%s", username)
            return Response({'error': 'Username must be at least 3 characters long'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email__iexact=email).exists():
            logger.warning("admin_register validation failed: duplicate email email=%s", email)
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username__iexact=username).exists():
            logger.warning("admin_register validation failed: duplicate username username=%s", username)
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )
        token, created = Token.objects.get_or_create(user=user)
        logger.info("admin_register succeeded user_id=%s username=%s email=%s", user.id, user.username, user.email)

        return Response({
            'token': token.key,
            'email': user.email,
            'username': user.username,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }, status=status.HTTP_201_CREATED)

    except DatabaseError as e:
        logger.error(f"Database error during admin_register: {str(e)}\n{traceback.format_exc()}")
        return Response({'error': 'Database connection failed. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e).lower():
            if 'username' in str(e):
                return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
            elif 'email' in str(e):
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        logger.error(f"Unexpected error in admin_register: {str(e)}\n{traceback.format_exc()}")
        return Response({'error': 'Registration failed. Please check your input and try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    identifier = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    logger.info("admin_login request received identifier=%s", identifier or "<empty>")

    if not identifier or not password:
        logger.warning("admin_login validation failed: missing identifier or password")
        return Response({'error': 'username/email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        candidates = User.objects.filter(
            Q(username__icontains=identifier) | Q(email__icontains=identifier),
            is_staff=True
        )
        user = next(
            (u for u in candidates if u.username.lower() == identifier.lower() or u.email.lower() == identifier.lower()),
            None
        )
        if not user:
            logger.warning("admin_login failed: user not found identifier=%s", identifier)
            return Response({'error': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error("admin_login lookup error identifier=%s error=%s\n%s", identifier, str(e), traceback.format_exc())
        return Response({'error': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        logger.warning("admin_login failed: bad password identifier=%s user_id=%s", identifier, user.id)
        return Response({'error': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    logger.info("admin_login succeeded user_id=%s username=%s email=%s", user.id, user.username, user.email)
    return Response({
        'token': token.key,
        'email': user.email,
        'username': user.username,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_quiz(request, quiz_id: int):
    try:
        quizset = QuizSet.objects.get(id=quiz_id, created_by=request.user)
    except QuizSet.DoesNotExist:
        return Response({"detail": "Quiz set not found"}, status=status.HTTP_404_NOT_FOUND)

    sessions_qs = SessionQuizSet.objects.filter(quiz_set=quizset).values_list('session_id', flat=True)
    participants_qs = Participant.objects.filter(session_id__in=sessions_qs).select_related('session').order_by('-score', 'total_response_time')

    total_questions = quizset.questions.count()

    all_participants = [
        {
            "id": p.id,
            "username": p.username,
            "score": int(p.score or 0),
            "time_seconds": int((p.total_response_time or 0) / 1000),
            "submitted": (p.score or 0) > 0 or (p.total_response_time or 0) > 0,
            "avatar_id": getattr(p, 'avatar_id', 0) or 0,
            "avatar_url": getattr(p, 'avatar_url', '') or '',
            "session_code": p.session.code if p.session else None,
            "joined_at": p.joined_at.isoformat() if getattr(p, 'joined_at', None) else None,
        }
        for p in participants_qs
    ]

    total_joined = len(all_participants)
    present_count = len([p for p in all_participants if p["submitted"]])
    absent_count = total_joined - present_count

    return Response({
        "quiz_title": quizset.title,
        "total_questions": total_questions,
        "total_joined": total_joined,
        "present_count": present_count,
        "absent_count": absent_count,
        "participants": all_participants,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_pdf(request):
    uploaded = request.FILES.get('file') or request.FILES.get('pdf')
    if not uploaded:
        return Response({"error": "No PDF file uploaded. Use field name 'file'"}, status=status.HTTP_400_BAD_REQUEST)

    content_type = getattr(uploaded, 'content_type', '') or ''
    if 'pdf' not in content_type and not uploaded.name.lower().endswith('.pdf'):
        return Response({"error": "Uploaded file is not a PDF"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded)
            parts = []
            for page in reader.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    continue
            extracted_text = "\n".join(parts)
        except Exception as e:
            return Response({"error": f"Failed to parse PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if not extracted_text.strip():
            return Response({"error": "No extractable text found in PDF"}, status=status.HTTP_400_BAD_REQUEST)

        questions = _parse_text_to_questions(extracted_text)
        guessed_title = _guess_title_from_text(extracted_text) or (uploaded.name.rsplit('.', 1)[0] if getattr(uploaded, 'name', None) else "")
        return Response({
            "questions": questions,
            "count": len(questions),
            "title": guessed_title
        })
    except Exception as e:
        return Response({"error": f"Server error processing PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def auto_create_questions_from_pdf(request):
    uploaded = request.FILES.get('file') or request.FILES.get('pdf')
    quiz_id = request.data.get('quiz_id')

    if not uploaded:
        return Response({"error": "No PDF file uploaded. Use field name 'file'"}, status=status.HTTP_400_BAD_REQUEST)
    if not quiz_id:
        return Response({"error": "quiz_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    content_type = getattr(uploaded, 'content_type', '') or ''
    if 'pdf' not in content_type and not uploaded.name.lower().endswith('.pdf'):
        return Response({"error": "Uploaded file is not a PDF"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quiz = QuizSet.objects.get(id=quiz_id, created_by=request.user)
    except QuizSet.DoesNotExist:
        return Response({"error": "Quiz not found or you don't have permission"}, status=status.HTTP_404_NOT_FOUND)

    try:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded)
            parts = []
            for page in reader.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    continue
            extracted_text = "\n".join(parts)
        except Exception as e:
            return Response({"error": f"Failed to parse PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if not extracted_text.strip():
            return Response({"error": "No extractable text found in PDF"}, status=status.HTTP_400_BAD_REQUEST)

        questions_data = _parse_text_to_questions(extracted_text)

        if not questions_data:
            return Response({"error": "No valid questions found in PDF"}, status=status.HTTP_400_BAD_REQUEST)

        created_questions = []
        question_order = 1

        for question_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=question_data['text'],
                timer_seconds=question_data.get('timer_seconds', 20),
                order=question_order
            )
            for choice_data in question_data.get('choices', []):
                Choice.objects.create(
                    question=question,
                    text=choice_data['text'],
                    is_correct=choice_data.get('is_correct', False)
                )
            created_questions.append({
                'id': question.id,
                'text': question.text,
                'order': question.order,
                'choices_count': len(question_data.get('choices', []))
            })
            question_order += 1

        return Response({
            "message": f"Successfully created {len(created_questions)} questions",
            "questions_created": len(created_questions),
            "quiz_id": quiz.id,
            "questions": created_questions
        })

    except Exception as e:
        return Response({"error": f"Server error processing PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import uuid, os
    ext = os.path.splitext(image.name)[1] or '.jpg'
    filename = f'avatars/{uuid.uuid4().hex}{ext}'
    path = default_storage.save(filename, ContentFile(image.read()))
    url = request.build_absolute_uri(settings.MEDIA_URL + path)
    return Response({'url': url})


@api_view(['GET'])
@permission_classes([AllowAny])
def my_answers(request, code):
    username = request.query_params.get('username', '').strip()
    if not username:
        return Response({"error": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        session = QuizSession.objects.get(code=code.strip().upper())
    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        participant = Participant.objects.get(session=session, username__iexact=username)
    except Participant.DoesNotExist:
        return Response({"error": "Participant not found"}, status=status.HTTP_404_NOT_FOUND)

    answer_map = {
        ar.question_id: ar
        for ar in participant.answers.select_related('choice').all()
    }

    # Build ordered question list safely: iterate SessionQuizSets in order,
    # then each quiz's questions ordered by (order, id). Deduplicate by question id.
    seen_ids = set()
    questions = []
    for sqs in SessionQuizSet.objects.filter(session=session).order_by('order').select_related('quiz_set'):
        for q in sqs.quiz_set.questions.prefetch_related('choices').order_by('order', 'id'):
            if q.id not in seen_ids:
                seen_ids.add(q.id)
                questions.append(q)

    result = []
    for i, q in enumerate(questions):
        correct_choice = next((c for c in q.choices.all() if c.is_correct), None)
        ar = answer_map.get(q.id)
        result.append({
            "question_number": i + 1,
            "question_text": q.text,
            "selected_choice_id": ar.choice_id if ar else None,
            "selected_choice_text": ar.choice.text if ar and ar.choice_id else None,
            "correct_choice_id": correct_choice.id if correct_choice else None,
            "correct_choice_text": correct_choice.text if correct_choice else None,
            "is_correct": ar.correct if ar else False,
        })

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_questions_to_session(request, code):
    try:
        session = QuizSession.objects.get(code=code, host=request.user, finished=False)
    except QuizSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    questions_data = request.data.get('questions', [])
    if not questions_data:
        return Response({"error": "No questions provided"}, status=status.HTTP_400_BAD_REQUEST)

    session_quiz = session.quiz_sets.filter(quiz_set__session_only=True).first()
    if session_quiz:
        quiz_set = session_quiz.quiz_set
    else:
        quiz_set = QuizSet.objects.create(
            created_by=request.user,
            title=f"Live Questions - {code}",
            session_only=True
        )
        SessionQuizSet.objects.create(session=session, quiz_set=quiz_set, order=999)

    created = []
    current_order = quiz_set.questions.count() + 1

    for q_data in questions_data:
        question = Question.objects.create(
            quiz=quiz_set,
            text=q_data['text'],
            timer_seconds=q_data.get('timer_seconds', 20),
            order=current_order
        )
        for choice_data in q_data.get('choices', []):
            Choice.objects.create(
                question=question,
                text=choice_data['text'],
                is_correct=choice_data.get('is_correct', False)
            )
        created.append({"id": question.id, "text": question.text})
        current_order += 1

    return Response({
        "message": f"{len(created)} question(s) added successfully",
        "questions_created": len(created),
        "questions": created
    }, status=status.HTTP_201_CREATED)
