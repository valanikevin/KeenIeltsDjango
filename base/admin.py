from django.contrib import admin
from base.models import Issue


class IssueAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'description')
    list_filter = ('user', 'type')
    search_fields = ('user', 'type')


admin.site.register(Issue, IssueAdmin)
