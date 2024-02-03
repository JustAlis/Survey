from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import *


class CustomAdmin(admin.ModelAdmin):
    actions = [
        'archive_selected', 
        'unarchive_selected'
    ]

    def has_delete_permission(self, request, obj=None):
        return False
    
    def archive_selected(self, request, queryset):
        for obj in queryset:
            obj.is_archived = True
            obj.save()

        self.message_user(request, format_html(
            'Выбранные объекты были успешно архивированы.'
        ), messages.SUCCESS)

        return HttpResponseRedirect(
            reverse(
                'admin:%s_%s_changelist' % (
                    self.model._meta.app_label,  
                    self.model._meta.model_name
                )
            )
        )
    
    archive_selected.short_description = 'Архивировать выбранные объекты'

    def unarchive_selected(self, request, queryset):
        for obj in queryset:
            obj.is_archived = False
            obj.save()

        self.message_user(request, format_html(
            'Выбранные объекты были успешно разархивированы.'
        ), messages.SUCCESS)

        return HttpResponseRedirect(
            reverse(
                'admin:%s_%s_changelist' % (
                    self.model._meta.app_label,  
                    self.model._meta.model_name
                )
            )
        )

    unarchive_selected.short_description = 'Разархивировать выбранные объекты'


class QuestionAdmin(CustomAdmin):
    ordering = ['survey']
    list_display = (
        'text', 
        'survey_link', 
        'is_archived', 
        'slug', 
        'previous_answers_link', 
        'answers_link'
    )
    list_display_links = (
        'text', 
        'survey_link', 
        'previous_answers_link', 
        'answers_link'
    ) 
    search_fields = (
        'text', 
        'previous_answers__text'
    )
    list_filter = (
        'survey',
        'is_archived'
    )
    list_per_page = 100
    exclude = ['slug']

    def get_queryset(self, request):
        self.queryset = super(
            QuestionAdmin,
            self
        ).get_queryset(
            request
        ).select_related(
            'survey', 
        )
        
        return self.queryset
    
    def survey_link(self, obj):
        survey = obj.survey
        if not survey:
            html = ''
        else:
            html = format_html(
                '<a href="{}">{}</a>'.format(
                    reverse(
                        'admin:tests_app_survey_change', 
                        args=[survey.pk]
                    ), 
                    survey
                )
            ) 
        return html
    
    survey_link.short_description = 'Опрос: '

    def previous_answers_link(self, obj):
        previous_answers = obj.previous_answers.filter(is_archived=False)
        if not previous_answers.exists():
            html = ''
        else:
            html = format_html(
                ', '.join(
                    '<a href="{}">{}</a>'.format(
                        reverse(
                            'admin:tests_app_answer_change', 
                            args=[previous_answer.pk]
                        ), 
                        previous_answer
                    ) for previous_answer in previous_answers
                )
            )
        return html
    
    previous_answers_link.short_description = 'Предыдущие ответы: '

    def answers_link(self, obj):
        answers = obj.answers.filter(is_archived=False)
        if not answers.exists():
            html = ''
        else:
            html = format_html(
                ', '.join(
                    '<a href="{}">{}</a>'.format(
                        reverse(
                            'admin:tests_app_answer_change', 
                            args=[answer.pk]
                        ), 
                        answer
                    ) for answer in answers
                )
            )
        return html
    
    answers_link.short_description = 'Ответы: '


class SurveyAdmin(CustomAdmin):
    ordering = ['title']
    list_display = (
        'title',
        'is_archived',
        'slug', 
        'answers_links', 
        'questions_links'
    )
    list_display_links = (
        'title',
        'answers_links',
        'questions_links'
    )
    search_fields = ('title',)
    list_filter = (
        'title', 
        'is_archived'
    )
    list_per_page = 100
    exclude = ['slug']
    
    def answers_links(self, obj):
        answers = obj.answers.filter(is_archived=False)
        if not answers.exists():
            html = ''
        else:
            html = format_html(
                ', '.join(
                    '<a href="{}">{}</a>'.format(
                        reverse(
                            'admin:tests_app_answer_change', 
                            args=[answer.pk]
                        ), 
                        answer
                    ) for answer in answers
                )
            )
        return html
    
    answers_links.short_description = 'Ответы: '

    def questions_links(self, obj):
        questions = obj.questions.filter(is_archived=False)
        if not questions.exists():
            html = ''
        else:
            html = format_html(
                ', '.join(
                    '<a href="{}">{}</a>'.format(
                        reverse(
                            'admin:tests_app_answer_change', 
                            args=[question.pk]
                        ), 
                        question
                    ) for question in questions
                )
            )
        return html
    
    questions_links.short_description = 'Вопросы: '


class AnswerAdmin(CustomAdmin):
    exclude=('users_answered',)

    ordering = ['survey']
    list_display = (
        'text', 
        'question_link', 
        'survey_link', 
        'is_archived',  
        'following_question_link'
    )
    list_display_links = (
        'text', 
        'question_link', 
        'survey_link', 
        'following_question_link'
    )
    search_fields = (
        'text', 
        'question__text', 
        'following_question__text'
    )
    list_filter = (
        'survey',
        'question', 
        'is_archived'
    )
    list_per_page = 100

    def get_queryset(self, request):
        self.queryset = super(
            AnswerAdmin,
            self
        ).get_queryset(
            request
        ).select_related(
            'survey', 
            'question', 
            'following_question'
        )
        return self.queryset

    def survey_link(self, obj):
        survey = obj.survey
        if not survey:
            html = ''
        else:
            html = format_html(
                '<a href="{}">{}</a>'.format(
                    reverse(
                        'admin:tests_app_survey_change', 
                        args=[survey.pk]
                    ), 
                    survey
                )
            ) 
        return html
    
    survey_link.short_description = 'Опрос: '

    def following_question_link(self, obj):
        following_question = obj.following_question
        if not following_question:
            html = ''
        else:
            html = format_html(
                '<a href="{}">{}</a>'.format(
                    reverse(
                        'admin:tests_app_question_change', 
                        args=[following_question.pk]
                    ), 
                    following_question
                )
            ) 
        return html
    
    following_question_link.short_description = 'Вопрос, следующий за этим ответом: '

    def question_link(self, obj):
        question = obj.question
        if not question:
            html = ''
        else:
            html = format_html(
                '<a href="{}">{}</a>'.format(
                    reverse(
                        'admin:tests_app_question_change', 
                        args=[question.pk]
                    ), 
                    question
                )
            ) 
        return html
    
    question_link.short_description = 'Вопрос: '


admin.site.register(Answer, AnswerAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
