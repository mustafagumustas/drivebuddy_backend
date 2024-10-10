from django.urls import path
from .views import (
    UserCreate,
    SignInView,
    start_conversation,
)

urlpatterns = [
    path("sign-up/", UserCreate.as_view(), name="sign_up"),
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("start_conversation/", start_conversation, name="start_conversation"),
]
