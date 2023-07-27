from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningTest, Book

# Inlines


class TestInline(admin.StackedInline):
    model = Test
    show_change_link = True
    extra = 1
    exclude = ['created_at', 'updated_at']


class ListeningSectionInline(admin.StackedInline):
    model = ListeningSection
    show_change_link = True
    extra = 1


class ListeningTestInline(admin.StackedInline):
    model = ListeningTest
    show_change_link = True
    extra = 1


# Admins

class BookAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [TestInline,]
    exclude = ['created_at', 'updated_at']


class TestAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    inlines = [ListeningTestInline]
    exclude = ['created_at', 'updated_at']


class ListeningTestAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [ListeningSectionInline]
    exclude = ['created_at', 'updated_at']


class ListeningSectionAdmin(admin.ModelAdmin):
    search_fields = ['test']
    exclude = ['created_at', 'updated_at']


admin.site.register(ListeningSection, ListeningSectionAdmin)
admin.site.register(ListeningTest, ListeningTestAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Book, BookAdmin)
