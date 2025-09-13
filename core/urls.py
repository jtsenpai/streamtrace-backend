from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, MeView, ProviderViewSet, SubscriptionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register("providers", ProviderViewSet, basename="provider")
router.register("subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("auth/register", RegisterView.as_view()),
    path("auth/login", TokenObtainPairView.as_view()),
    path("auth/refresh", TokenRefreshView.as_view()),
    path("me", MeView.as_view()),
    path("health", lambda r: __import__("django").http.HttpResponse('{"status": "ok"}', content_type="application/json")),
    path("", include(router.urls)),
]
