from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningTest, Category


class ListeningSectionInline(admin.StackedInline):
    model = ListeningSection
    show_change_link = True


class ListeningTestInline(admin.StackedInline):
    model = ListeningTest
    show_change_link = True


class TestAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    inlines = [ListeningTestInline]


class ListeningTestAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [ListeningSectionInline]


admin.site.register(ListeningTest, ListeningTestAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Category)
