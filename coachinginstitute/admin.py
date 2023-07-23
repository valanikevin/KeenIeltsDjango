from django.contrib import admin
from coachinginstitute.models import CoachingInstitute, Tutor

# Register your models here.


class TutorInline(admin.StackedInline):
    model = Tutor


class CoachingInstituteAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    inlines = [TutorInline,]


admin.site.register(CoachingInstitute, CoachingInstituteAdmin)
