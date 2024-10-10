from django.contrib.auth import get_user_model, authenticate
from accounts.voice_activity_detection import SpeechRecorder
from .serializers import UsersSerializer, SignInSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from django.contrib.auth.models import User
from rest_framework import permissions
from django.http import JsonResponse
from accounts.main import main_loop, return_text
from threading import Thread
from mem0 import Memory
import logging
import dotenv
import os
from django.conf import settings
from pydub import AudioSegment
import io
from django.http import HttpResponse

User = get_user_model()

logger = logging.getLogger(__name__)


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Validation Errors:", serializer.errors)  # Log the errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            return Response(
                {
                    "message": "Login successful!",
                    "user": {"username": user.username, "email": user.email},
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )


# server neo4j
load_status = dotenv.load_dotenv("variables.txt")
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
USR = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": URI, "username": USR, "password": PASSWORD},
    },
    "version": "v1.1",
}


@api_view(["POST"])
def start_conversation(request):
    print("Reached start_conversation")
    mem0_user_id = "mustafa_gumustas"
    first_run = request.data.get("first_run", True)
    conversation_thread = Thread(target=main_loop)
    conversation_thread.start()
    return JsonResponse({"message": "Conversation loop started."})
