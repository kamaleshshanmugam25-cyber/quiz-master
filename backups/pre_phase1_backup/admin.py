from django.contrib import admin
from .models import QuizSet, Question, Choice, User, Participant


# Choice inline under Question
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    min_num = 2
    max_num = 6
    fields = ('text', 'is_correct')
    show_change_link = True

# Question inline under QuizSet
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'timer_seconds')
    show_change_link = True  # choices will be edited in QuestionAdmin

# Admin for Question
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz_title', 'timer_seconds')
    inlines = [ChoiceInline]  # manage choices here
    list_filter = ('quiz',)
    search_fields = ('text',)

    def quiz_title(self, obj):
        return obj.quiz.title
    quiz_title.short_description = 'Quiz'

# Admin for QuizSet
class QuizSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    inlines = [QuestionInline]  # only questions, choices edited separately
    search_fields = ('title',)

# Register
admin.site.register(QuizSet, QuizSetAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "username")


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("username", "session", "score", "total_response_time", "joined_at")
    list_filter = ("session",)
    search_fields = ("username", "session__code")