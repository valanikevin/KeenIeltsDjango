from django.contrib import admin
from coachinginstitute.models import CoachingInstitute

# Register your models here.


class CoachingInstituteAdmin(admin.ModelAdmin):
    search_fields = ['name',]


admin.site.register(CoachingInstitute, CoachingInstituteAdmin)
