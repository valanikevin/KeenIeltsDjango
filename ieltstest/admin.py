from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningModule, Book, ListeningAttempt, QuestionType, ReadingModule, ReadingSection, ReadingAttempt, WritingAttempt, WritingModule, WritingSection, SpeakingAttempt, SpeakingModule, SpeakingSection, SpeakingSectionQuestion, SpeakingAttemptAudio, FullTestAttempt, CoachingInstitute


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


class SpeakingAttemptAudioInline(admin.StackedInline):
    model = SpeakingAttemptAudio
    show_change_link = True

# Admins


class BookAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [TestInline,]
    exclude = ['created_at', 'updated_at']
    readonly_fields = ['slug']
    list_display = ['name', 'copyright', 'slug', 'status', 'priority', ]
    list_editable = ['status', 'priority']


class TestAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    inlines = [ListeningModuleInline, ReadingModuleInline,
               WritingModuleInline, SpeakingModuleInline]
    exclude = ['created_at', 'updated_at']
    list_display = ['name', 'book', 'status', 'slug', ]
    list_editable = ['status', ]


class ModuleAdmin(admin.ModelAdmin):
    search_fields = ['name']
    exclude = ['created_at', 'updated_at']
    list_display = ["name", 'status', "test",
                    "book_name", "test_type", 'slug', ]
    list_editable = ['status', ]

    class Meta:
        abstract = True

    def book_name(self, obj):
        return obj.test.book.name


class SectionAdmin(admin.ModelAdmin):

    exclude = ['created_at', 'updated_at']

    def get_list_display(self, request):
        # Define common fields for list_display here
        return []

    class Meta:
        abstract = True


class ListeningSectionAdmin(SectionAdmin):
    readonly_fields = ['total_questions']

    def get_list_display(self, request):
        # Include base class list_display and add custom fields
        return super(ListeningSectionAdmin, self).get_list_display(request) + ['name', 'total_questions', 'listening_module', 'book_name']

    def book_name(self, obj):
        return obj.listening_module.test.book.name


class ReadingSectionAdmin(SectionAdmin):
    readonly_fields = ['total_questions']

    def get_list_display(self, request):
        # Include base class list_display and add custom fields
        return super(ReadingSectionAdmin, self).get_list_display(request) + ['name', 'total_questions', 'reading_module', 'book_name']

    def book_name(self, obj):
        return obj.reading_module.test.book.name


class SpeakingSectionAdmin(SectionAdmin):
    list_display = ['name', 'speaking_module', ]
    inlines = [SpeakingSectionQuestionInline, ]


class ListeningModuleAdmin(ModuleAdmin):
    readonly_fields = ['total_questions']
    inlines = [ListeningSectionInline]

    def get_list_display(self, request):
        return super(ListeningModuleAdmin, self).get_list_display(request) + ['total_questions']


class ReadingModuleAdmin(ModuleAdmin):
    readonly_fields = ['total_questions']
    inlines = [ReadingSectionInline]

    def get_list_display(self, request):
        return super(ReadingModuleAdmin, self).get_list_display(request) + ['total_questions']


class WritingModuleAdmin(ModuleAdmin):
    inlines = [WritingSectionInline]


class SpeakingModuleAdmin(ModuleAdmin):
    inlines = [SpeakingSectionInline]


class AttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'book_name', 'module', 'slug', 'status', 'bands']
    list_filter = ['status']

    class Meta:
        abstract = True

    def book_name(self, obj):
        return obj.module.test.book.name


class ListeningAttemptAdmin(AttemptAdmin):
    pass


class ReadingAttemptAdmin(AttemptAdmin):
    pass


class WritingAttemptAdmin(AttemptAdmin):
    pass


class SpeakingAttemptAdmin(AttemptAdmin):
    inlines = [SpeakingAttemptAudioInline,]


class FullTestAttemptAdmin(AttemptAdmin):
    list_display = ['user', 'slug', 'status', 'bands']


admin.site.register(Test, TestAdmin)
admin.site.register(Book, BookAdmin)

# Listening
admin.site.register(ListeningAttempt, ListeningAttemptAdmin)
admin.site.register(QuestionType)
admin.site.register(ListeningSection, ListeningSectionAdmin)
admin.site.register(ListeningModule, ListeningModuleAdmin)

# Reading
admin.site.register(ReadingModule, ReadingModuleAdmin)
admin.site.register(ReadingSection, ReadingSectionAdmin)
admin.site.register(ReadingAttempt, ReadingAttemptAdmin)

# Writing
admin.site.register(WritingModule, WritingModuleAdmin)
admin.site.register(WritingSection, SectionAdmin)
admin.site.register(WritingAttempt, WritingAttemptAdmin)

# Speaking
admin.site.register(SpeakingModule, SpeakingModuleAdmin)
admin.site.register(SpeakingSection, SpeakingSectionAdmin)
admin.site.register(SpeakingAttempt, SpeakingAttemptAdmin)

# Full Test
admin.site.register(FullTestAttempt, FullTestAttemptAdmin)
