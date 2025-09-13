from rest_framework import generics, permissions, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, timedelta
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, MeSerializer, ProviderSerializer, SubscriptionSerializer
from .models import Provider, Subscription

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response(MeSerializer(request.user).data)

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allow the world to READ (GET/HEAD/OPTIONS), but only authenticated users can WRITE.
    Great for demos/portfolios where you want public visibility.
    """
    def has_permission(self, request, view):
        safe = request.method in ("GET", "HEAD", "OPTIONS")
        return True if safe else (request.user and request.user.is_authenticated)
    
class ProviderViewSet(viewsets.ModelViewSet):
    """
    RESTful endpoints at /api/providers/ via router:
      - GET    /api/providers/          -> list (supports ?search= & ?ordering=)
      - POST   /api/providers/          -> create   (auth required)
      - GET    /api/providers/{id}/     -> retrieve
      - PATCH  /api/providers/{id}/     -> partial update (auth required)
      - PUT    /api/providers/{id}/     -> full update    (auth required)
      - DELETE /api/providers/{id}/     -> delete         (auth required)
    """
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # This enables the Search and Ordering Filters
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["next_renewal_date","price","created_at"]
    ordering = ["next_renewal_date"]

    def get_queryset(self):
        qs = Subscription.objects.filter(user=self.request.user).select_related("provider")
        provider = self.request.query_params.get("provider")
        if property:
            qs = qs.filter(property_id=provider)
        due_in = self.request.query_params.get("due_in_days")
        if due_in:
            try:
                n = int(due_in)
                qs = qs.filter(next_renewal_date__lte=date.today() + timedelta(days=n))
            except ValueError:
                pass
        return qs
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)