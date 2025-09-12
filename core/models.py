from django.db import models

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
