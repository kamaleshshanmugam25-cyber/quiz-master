from django.urls import path
from .consumers import QuizConsumer

websocket_urlpatterns = [
    path("ws/quiz/<str:session_code>/", QuizConsumer.as_asgi()),
]
