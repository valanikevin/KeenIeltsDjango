from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningModule, Book, ListeningAttempt, QuestionType, ReadingModule, ReadingSection, ReadingAttempt, WritingAttempt, WritingModule, WritingSection, SpeakingAttempt, SpeakingModule, SpeakingSection, SpeakingSectionQuestion

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


class WritingModuleInline(admin.StackedInline):
    model = WritingModule
    show_change_link = True
    extra = 1


class WritingSectionInline(admin.StackedInline):
    model = WritingSection
    show_change_link = True
    extra = 1


class SpeakingModuleInline(admin.StackedInline):
    model = SpeakingModule
    show_change_link = True
    extra = 1


class SpeakingSectionInline(admin.StackedInline):
    model = SpeakingSection
    show_change_link = True
    extra = 1


class SpeakingSectionQuestionInline(admin.StackedInline):
    model = SpeakingSectionQuestion
    show_change_link = True,
    extra = 3

# Admins


class BookAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [TestInline,]
    exclude = ['created_at', 'updated_at']


class TestAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    inlines = [ListeningModuleInline, ReadingModuleInline,
               WritingModuleInline, SpeakingModuleInline]
    exclude = ['created_at', 'updated_at']


class ModuleAdmin(admin.ModelAdmin):
    search_fields = ['name']
    exclude = ['created_at', 'updated_at']
    list_display = ['name', 'slug']

    class Meta:
        abstract = True


class SectionAdmin(admin.ModelAdmin):
    search_fields = ['test']
    exclude = ['created_at', 'updated_at', ]
    list_display = ['name']

    class Meta:
        abstract = True


class SpeakingSectionAdmin(SectionAdmin):
    inlines = [SpeakingSectionQuestionInline, ]


class ListeningModuleAdmin(ModuleAdmin):
    readonly_fields = ['total_questions']
    inlines = [ListeningSectionInline]


class ReadingModuleAdmin(ModuleAdmin):
    readonly_fields = ['total_questions']
    inlines = [ReadingSectionInline]


class WritingModuleAdmin(ModuleAdmin):
    inlines = [WritingSectionInline]


class SpeakingModuleAdmin(ModuleAdmin):
    inlines = [SpeakingSectionInline]


class ListeningAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'status', 'bands']


class ReadingAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'status', 'bands']


class WritingAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'status', 'bands']


class SpeakingAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'status', 'bands']


admin.site.register(Test, TestAdmin)
admin.site.register(Book, BookAdmin)

# Listening
admin.site.register(ListeningAttempt, ListeningAttemptAdmin)
admin.site.register(QuestionType)
admin.site.register(ListeningSection, SectionAdmin)
admin.site.register(ListeningModule, ListeningModuleAdmin)

# Reading
admin.site.register(ReadingModule, ReadingModuleAdmin)
admin.site.register(ReadingSection, SectionAdmin)
admin.site.register(ReadingAttempt, ReadingAttemptAdmin)

# Writing
admin.site.register(WritingModule, WritingModuleAdmin)
admin.site.register(WritingSection, SectionAdmin)
admin.site.register(WritingAttempt, WritingAttemptAdmin)

# Speaking
admin.site.register(SpeakingModule, SpeakingModuleAdmin)
admin.site.register(SpeakingSection, SpeakingSectionAdmin)
admin.site.register(SpeakingAttempt, SpeakingAttemptAdmin)
