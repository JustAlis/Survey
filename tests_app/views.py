# from django.shortcuts import render
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Prefetch, Count
from .utils import parse_sql_result
from .sql import sql_get_survey_statistics
from .models import *


def survey_list(request):
    surveys = Survey.objects.only('title', 'slug', 'pk')
    return render(request, 'tests_app/survey_list.html', {'surveys': surveys})


def survey_detail(request, slug):
    # чтобы не делать дополнительное поле с отметкой "первый вопрос в опросе"
    # приходится выполнять несколько запросов для обнаружения первого вопроса
    survey_queryset = Survey.objects.only(
        'title', 
        'pk', 
        'slug'
    ).filter(slug=slug)

    previous_answers_queryset = Answer.objects.only(
        'pk', 
        'is_archived',
        'following_question'
    ).filter(
        is_archived = False
    )

    question_queryset = Question.objects.prefetch_related(
        Prefetch(
            'previous_answers',
            queryset = previous_answers_queryset
        )
    ).only(
        'survey', 
        'pk',
        'slug',
        'is_archived',
        'text'
    ).annotate(
        num_answers=Count(
            'previous_answers'
        )
    ).filter(
        is_archived=False,
        num_answers=0
    )

    survey = survey_queryset.prefetch_related(
        Prefetch(
            'questions', 
            queryset=question_queryset
        )
    ).filter(
        is_archived=False
    ).first()


    return render(request, 'tests_app/survey_detail.html', {'survey': survey})


def question_detail(request, slug):
    answers_queryset = Answer.objects.select_related(
        'following_question'
    ).only(
        'pk', 
        'is_archived',
        'text',
        'question',
        'following_question__slug'
    ).filter(
        is_archived = False
    )

    question = Question.objects.filter(
        slug=slug
    ).select_related(
        'survey'
    ).prefetch_related(
        Prefetch(
            'answers',
            queryset=answers_queryset
        )
    ).first()

    if request.method == "POST":

        users_input = request.POST.get('input')
        answered_question = request.POST.get('question')
        parsed_input = users_input.split(',')
        users_answer = parsed_input[1]
        redirect_slug = parsed_input[0]
        user_pk = request.user.pk

        if not users_answer or not answered_question or not user_pk:
            raise ValueError('Некорректные данные в запросе')
        
        existing_answer = UsersAnswers.objects.filter(
            user_pk = user_pk, 
            question_pk = answered_question
        ).first()

        if not existing_answer:
            UsersAnswers.objects.create(
                user_pk = user_pk, 
                question_pk = answered_question,
                answer_pk = users_answer
            )
        else:
            existing_answer.answer_pk = users_answer
            existing_answer.save()

        if redirect_slug:
            return redirect('question', slug=redirect_slug)
        
        else:
            redirect_slug = request.POST.get('redirect_statistics')
            return redirect('statistics', slug=redirect_slug)
        

    return render(request, 'tests_app/question_detail.html', {'question': question})


def survey_statistics(request, slug):
    survey = Survey.objects.filter(slug=slug).first()
    raw_statistics = sql_get_survey_statistics(survey.pk)
    statistics = parse_sql_result(raw_statistics)
    statistics['title'] = survey.title
    return render(request, 'tests_app/survey_statistics.html', {'statistics': statistics})


class RegisterUser(CreateView):
    form_class = UserCreationForm
    template_name = 'tests_app/forms/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'tests_app/forms/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')
