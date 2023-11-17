from django.contrib import admin
from coachinginstitute.models import CoachingInstitute, Tutor
from custom_user.admin import StudentInline
# Register your models here.


class TutorInline(admin.StackedInline):
    model = Tutor
    autocomplete_fields = ['user']


class CoachingInstituteAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    inlines = [TutorInline, StudentInline]


admin.site.register(CoachingInstitute, CoachingInstituteAdmin)
