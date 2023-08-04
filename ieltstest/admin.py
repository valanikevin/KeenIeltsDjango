from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningModule, Book, ListeningAttempt

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
    list_display = ['name', 'slug']
    readonly_fields = ['total_questions']


class ListeningSectionAdmin(admin.ModelAdmin):
    search_fields = ['test']
    exclude = ['created_at', 'updated_at', ]
    list_display = ['name']
    readonly_fields = ['total_questions']


class ListeningAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'status']
    

admin.site.register(ListeningSection, ListeningSectionAdmin)
admin.site.register(ListeningModule, ListeningModuleAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(ListeningAttempt, ListeningAttemptAdmin)
