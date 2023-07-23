from django.contrib import admin
from django_use_email_as_username.admin import BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User
from student.models import Student

from coachinginstitute.models import Tutor


class TutorInline(admin.StackedInline):
    model = Tutor
    autocomplete_fields = ['user', 'institute']


class StudentInline(admin.StackedInline):
    model = Student
    autocomplete_fields = ['user', 'institute']


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),

    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": (
            "email", "password1", "password2")}),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    inlines = [StudentInline, TutorInline]


admin.site.register(User, UserAdmin)
