from django.contrib import admin
from base.models import Issue, CommentMain, CommentItem, AiResponse


class IssueAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'description')
    list_filter = ('user', 'type')
    search_fields = ('user', 'type')


class CommentItemInline(admin.StackedInline):
    model = CommentItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class CommentMainAdmin(admin.ModelAdmin):
    inlines = [CommentItemInline,]
    list_display = ('unique_id',)
    search_fields = ('unique_id',)


class AiResponseAdmin(admin.ModelAdmin):
    list_display = ('info', 'category', 'status')
    list_filter = ('status', 'category')
    search_fields = ('info', 'status')


admin.site.register(Issue, IssueAdmin)
admin.site.register(CommentMain, CommentMainAdmin)
admin.site.register(AiResponse, AiResponseAdmin)
