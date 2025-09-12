from django.db import models

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class Provider(TimeStamped):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
