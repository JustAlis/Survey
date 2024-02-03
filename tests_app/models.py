
from django.db import models
from django.urls import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from unidecode import unidecode
from collections.abc import Iterable
from typing import Any
from .utils import unbond_keys_except_users

class Survey(models.Model):
    title = models.CharField(
        max_length=255,  
        verbose_name = 'Опрос: '
    )
    is_archived = models.BooleanField(
        default=False, 
        verbose_name = 'Заархивирован: '
    )
    slug = models.SlugField(
        null=True, 
        blank=True, 
        unique=True, 
        verbose_name = 'Слаг: '
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.title))
        super(Survey, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('survey', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(
        Survey, 
        null=True, 
        on_delete=models.SET_NULL, 
        related_name='questions', 
        verbose_name='Опрос: '
    )
    text = models.CharField(
        max_length=255, 
        verbose_name = 'Вопрос: '
    )
    is_archived = models.BooleanField(
        default=False,
        verbose_name = 'Заархивирован: '
    )
    slug = models.SlugField(
        null=True, 
        blank=True, 
        unique=True, 
        verbose_name = 'Слаг: '
    )
    
    def save(self, *args, **kwargs):
        self.slug = self.survey.slug + '-' + slugify(unidecode(self.text))
        super(Question, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('question', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.text
    

class Answer(models.Model):
    survey = models.ForeignKey(
        Survey, null=True, 
        on_delete=models.SET_NULL, 
        related_name='answers', 
        verbose_name='Опрос: '
    )
    is_archived = models.BooleanField(
        default=False, 
        verbose_name = 'Заархивирован: '
    )
    question = models.ForeignKey(
        Question, 
        null=True, 
        on_delete=models.SET_NULL, 
        related_name='answers', 
        verbose_name='Вопрос: '
    )
    text = models.CharField(
        max_length=255, 
        verbose_name = 'Ответ: '
    )
    following_question = models.ForeignKey(
        Question, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='previous_answers', 
        verbose_name='Вопрос, следующий за этим ответом: '
    )

    def __str__(self):
        return self.text


# по сути это кастомная таблица m2m которая позволит проще и быстрее обрабатывать
# ответы пользователей, при этом не занимая сильно больше места, чем стандартная m2m
# таблица, которая в любом случае нужен для учёта ответов пользователей.
# Да, она больше(на 1 столбец интов), но любая операция сразу теряет в комплексности
class UsersAnswers(models.Model):
    user_pk = models.IntegerField(null=False, blank=False, verbose_name='ID пользователя: ')
    question_pk = models.IntegerField(null=False, blank=False, verbose_name='ID вопроса: ')
    answer_pk = models.IntegerField(null=False, blank=False, verbose_name='ID ответа: ')
    

# в случае если изменено важное по смыслу содержимое объекта ответа, 
# то мы не можем считать ответы пользователей валидными, но сохраняем
# их ответы, перевязывая все связи в цепочке опроса на новый объект
# оставляя связь с ответами у старого объекта ответа
@receiver(pre_save, sender=Answer)
def unbond_keys_if_changed(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    if (
        obj.text == instance.text and
        obj.question == instance.question and
        obj.survey == instance.survey
    ):
        return

    unbond_keys_except_users(instance=instance, model=Answer)
    return

@receiver(pre_save, sender=Survey)
def do_something_if_changed(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    if obj.title == instance.title:
        return
    
    all_answers = Answer.objects.filter(survey=instance)
    for answer in all_answers:
        unbond_keys_except_users(instance=answer, model=Answer)

    return

@receiver(pre_save, sender=Question)
def do_something_if_changed(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    if (
        obj.text == instance.text and
        obj.survey == instance.survey
    ):
        print("ТНЕ ПОНЯЛ НАХУЙ")

        return

    all_answers = Answer.objects.filter(question=instance)
    for answer in all_answers:
        unbond_keys_except_users(instance=answer, model=Answer)

    return
        
# вопрос без ответов - проблема админа
# сломанная цепочка - проблема админа