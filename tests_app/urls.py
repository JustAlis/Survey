"""
URL configuration for test_test project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import survey_list, survey_detail, question_detail, survey_statistics, LoginUser, RegisterUser, logout_user
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', survey_list, name='home'),
    path('survey/<slug:slug>/', login_required(survey_detail), name='survey'),
    path('question/<slug:slug>/', login_required(question_detail), name='question'),
    path('statistics/<slug:slug>/', login_required(survey_statistics), name='statistics'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', login_required(logout_user), name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
]