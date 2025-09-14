from rest_framework import generics, permissions, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, MeSerializer, ProviderSerializer, SubscriptionSerializer
from .models import Provider, Subscription
from .utils import monthly_equivalent, yearly_equivalent

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



class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary?days=14
    Returns:
      {
        "totals": {"monthly": "XX.XX", "yearly": "YYY.YY", "count": N},
        "upcoming": [ {id, provider_name, plan_name, next_renewal_date, price, currency}, ... ],
        "by_provider": [ {"provider": "Netflix", "count": 3, "monthly": "19.98"} ]
      }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = request.query_params.get("days") or "14"
        try:
            window = int(days)
        except ValueError:
            window = 14

        subs = (
            Subscription.objects
            .filter(user=request.user)
            .select_related("provider")
        )

        # Totals
        monthly_total = Decimal("0")
        yearly_total = Decimal("0")
        for s in subs:
            monthly_total += monthly_equivalent(s.price, s.billing_cycle, s.custom_cycle_days)
            yearly_total  += yearly_equivalent(s.price, s.billing_cycle, s.custom_cycle_days)

        # Upcoming renewals
        soon = (
            subs.filter(next_renewal_date__lte=date.today() + timedelta(days=window))
                .order_by("next_renewal_date")[:20]
        )
        upcoming = [
            {
                "id": s.id,
                "provider_name": s.provider.name if s.provider_id else None,
                "plan_name": s.plan_name,
                "next_renewal_date": s.next_renewal_date,
                "price": str(s.price),
                "currency": s.currency,
                "auto_renew": s.auto_renew,
            }
            for s in soon
        ]

        # By provider (small rollup)
        tallies = {}
        for s in subs:
            key = s.provider.name if s.provider_id else "Unknown"
            m = monthly_equivalent(s.price, s.billing_cycle, s.custom_cycle_days)
            if key not in tallies:
                tallies[key] = {"provider": key, "count": 0, "monthly": Decimal("0")}
            tallies[key]["count"] += 1
            tallies[key]["monthly"] += m

        by_provider = [
            {"provider": k, "count": v["count"], "monthly": f"{v['monthly']:.2f}"}
            for k, v in sorted(tallies.items(), key=lambda kv: kv[0].lower())
        ]

        return Response({
            "totals": {
                "monthly": f"{monthly_total:.2f}",
                "yearly": f"{yearly_total:.2f}",
                "count": subs.count(),
            },
            "upcoming": upcoming,
            "by_provider": by_provider,
        })