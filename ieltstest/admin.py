from django.contrib import admin
from ieltstest.models import Test, ListeningSection, ListeningTest, Category, ListeningQuestionSet

# Inlines


class ListeningQuestionSetInline(admin.StackedInline):
    model = ListeningQuestionSet
    show_change_link = True
    extra = 1


class ListeningSectionInline(admin.StackedInline):
    model = ListeningSection
    show_change_link = True


class ListeningTestInline(admin.StackedInline):
    model = ListeningTest
    show_change_link = True


# Admins

class TestAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id']
    inlines = [ListeningTestInline]


class ListeningTestAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [ListeningSectionInline]


class ListeningQuestionSetAdmin(admin.ModelAdmin):
    search_fields = ['name', 'title']


class ListeningSectionAdmin(admin.ModelAdmin):
    search_fields = ['test']
    inlines = [ListeningQuestionSetInline,]


admin.site.register(ListeningSection, ListeningSectionAdmin)
admin.site.register(ListeningQuestionSet, ListeningQuestionSetAdmin)
admin.site.register(ListeningTest, ListeningTestAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Category)
