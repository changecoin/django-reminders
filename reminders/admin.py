from django.contrib import admin

from models import Dismissal


class DismissalAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "label", "dismissed_at"]
    search_fields = ['id', 'user__username', 'user__first_name', 'user__last_name', 'label']

admin.site.register(Dismissal, DismissalAdmin)