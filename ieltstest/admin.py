from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningModule, Book

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


class ListeningModuleInline(admin.StackedInline):
    model = ListeningModule
    show_change_link = True
    extra = 1


# Admins

class BookAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [TestInline,]
    exclude = ['created_at', 'updated_at']


class TestAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    inlines = [ListeningModuleInline]
    exclude = ['created_at', 'updated_at']


class ListeningModuleAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [ListeningSectionInline]
    exclude = ['created_at', 'updated_at']


class ListeningSectionAdmin(admin.ModelAdmin):
    search_fields = ['test']
    exclude = ['created_at', 'updated_at']


admin.site.register(ListeningSection, ListeningSectionAdmin)
admin.site.register(ListeningModule, ListeningModuleAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Book, BookAdmin)
