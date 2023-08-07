from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningModule, Book, ListeningAttempt, ListeningSectionQuestionType, ReadingModule, ReadingSection

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


class ReadingModuleInline(admin.StackedInline):
    model = ReadingModule
    show_change_link = True
    extra = 1


class ReadingSectionInline(admin.StackedInline):
    model = ReadingSection
    show_change_link = True
    extra = 1

# Admins


class BookAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [TestInline,]
    exclude = ['created_at', 'updated_at']


class TestAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    inlines = [ListeningModuleInline, ReadingModuleInline]
    exclude = ['created_at', 'updated_at']


class ModuleAdmin(admin.ModelAdmin):
    search_fields = ['name']
    exclude = ['created_at', 'updated_at']
    list_display = ['name', 'slug']
    readonly_fields = ['total_questions']

    class Meta:
        abstract = True


class SectionAdmin(admin.ModelAdmin):
    search_fields = ['test']
    exclude = ['created_at', 'updated_at', ]
    list_display = ['name']
    readonly_fields = ['total_questions']

    class Meta:
        abstract = True


class ListeningModuleAdmin(ModuleAdmin):
    inlines = [ListeningSectionInline]


class ReadingModuleAdmin(ModuleAdmin):
    inlines = [ReadingSectionInline]


class ListeningAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'status', 'bands']


admin.site.register(Test, TestAdmin)
admin.site.register(Book, BookAdmin)

# Listening
admin.site.register(ListeningAttempt, ListeningAttemptAdmin)
admin.site.register(ListeningSectionQuestionType)
admin.site.register(ListeningSection, SectionAdmin)
admin.site.register(ListeningModule, ListeningModuleAdmin)

# Reading
admin.site.register(ReadingModule, ReadingModuleAdmin)
admin.site.register(ReadingSection, SectionAdmin)
