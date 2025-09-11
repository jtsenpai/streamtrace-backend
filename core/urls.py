from django.urls import path
from .views import RegisterView, MeView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("auth/register", RegisterView.as_view()),
    path("auth/login", TokenObtainPairView.as_view()),
    path("auth/refresh", TokenRefreshView.as_view()),
    path("me", MeView.as_view()),
    path("health", lambda r: __import__("django").http.HttpResponse('{"status": "ok"}', content_type="application/json")),
]
