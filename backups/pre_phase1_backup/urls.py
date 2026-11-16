from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from .views import (
    QuizSetViewSet, create_session, admin_login, admin_register, quizsets,
    quizset_detail, question_detail, session_quiz, validate_pin, join_session,
    session_participants, start_quiz, end_quiz, end_session, next_quiz_set,
    next_question, active_session, reports_quiz, check_username_availability,
    leave_session, upload_pdf, auto_create_questions_from_pdf,
    add_questions_to_session, upload_avatar, my_answers
)

router = DefaultRouter()
router.register(r'quizsets', QuizSetViewSet, basename='quizset')

urlpatterns = [
    path('', include(router.urls)),
    path('create_session/', create_session),
    path('admin-login/', csrf_exempt(admin_login)),
    path('admin-register/', csrf_exempt(admin_register)),
    path('quizsets/', quizsets),
    path('quizsets/<int:quizset_id>/', quizset_detail),
    path('quizsets/<int:quizset_id>/questions/<int:question_id>/', question_detail),
    path('validate-pin/<str:code>/', validate_pin),
    path('join/<str:code>/', csrf_exempt(join_session)),
    path('leave/<str:code>/', csrf_exempt(leave_session)),
    path('session/<str:code>/participants/', session_participants),
    path('session/<str:code>/check-username/<str:username>/', check_username_availability),
    path('session/<str:code>/check-username/', check_username_availability),
    path('check-username/<str:code>/', check_username_availability),
    path('session/<str:code>/start/', start_quiz),
    path('session/<str:code>/end/', end_quiz),
    path('session/<str:code>/end-session/', end_session),
    path('session/<str:code>/next/', next_quiz_set),
    path('session/<str:code>/next-question/', next_question),
    path('session/<str:code>/add-questions/', add_questions_to_session),
    path('session/<str:code>/my-answers/', my_answers),
    path('session/<str:code>/', session_quiz),   # ← MUST be last
    path('active_session/', active_session),
    path('reports/<int:quiz_id>/', reports_quiz),
    path('quiz/upload-pdf/', upload_pdf),
    path('quiz/auto-create-questions/', auto_create_questions_from_pdf),
    path('upload-avatar/', csrf_exempt(upload_avatar)),
]