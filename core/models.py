from django.conf import settings
from django.db import models
from datetime import date, timedelta

class TimeStamped(models.Model):
    """
    Reusable base model that auto-adds created_at/updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class Provider(TimeStamped):
    """
    A streaming/media provider (e.g., Netflix, Spotify).
    name: unique + indexed for fast searches and clean duplicates prevention.
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"
    BILLING_CHOICES = [(MONTHLY, "Monthly"), (YEARLY, "Yearly"), (CUSTOM, "Custom")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    provider = models.ForeignKey("core.Provider", on_delete=models.CASCADE, related_name="subscriptions")
    plan_name = models.CharField(max_length=120, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    billing_cycle = models.CharField(max_length=12, choices=BILLING_CHOICES, default=MONTHLY)
    start_date = models.DateField()
    custom_cycle_days = models.PositiveIntegerField(default=0)
    next_renewal_date = models.DateField(db_index=True, blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "nex_renewal_date"]),
            models.Index(fields=["users", "provider"]),
        ]
        ordering = ["next_renewal_date", "provider__name"]

    def __str__(self):
        return f"{self.user} • {self.provider.name} • {self.plan_name or self.billing_cycle}"
    
    def compute_next_renewal(self):
        if self.billing_cycle == self.MONTHLY:
            return self.start_date + timedelta(days=30)
        if self.billing_cycle == self.YEARLY:
            return self.start_date + timedelta(days=365)
        if self.billing_cycle == self.CUSTOM and self.custom_cycle_days > 0:
            return self.start_date + timedelta(days=self.custom_cycle_days)
        return self.start_date + timedelta(days=30)
    
    def save(self, *args, **kwargs):
        if not self.next_renewal_date:
            self.next_renewal_date = self.compute_next_renewal()
        super().save(*args, **kwargs)