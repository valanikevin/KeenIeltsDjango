from django.contrib import admin
from student.models import Student, OverallPerformanceFeedback


class OverallPerformanceFeedbackInline(admin.StackedInline):
    model = OverallPerformanceFeedback
    show_change_link = True
    extra = 1


class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'institute', 'type', 'bandsTarget')
    inlines = [OverallPerformanceFeedbackInline]


admin.site.register(Student, StudentAdmin)
