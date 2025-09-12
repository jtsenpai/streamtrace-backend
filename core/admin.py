from django.contrib import admin
from .models import Provider

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
   list_display = ("name", "url", "created_at")
   search_fields = ("name",)
   ordering = ("name",)
