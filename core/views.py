from rest_framework import generics, permissions, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, MeSerializer, ProviderSerializer
from .models import Provider

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