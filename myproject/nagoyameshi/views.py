from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from .models import Restaurant, User, UserActivateTokens
from .forms import SignUpForm, PasswordresetForm

import environ
import os

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'http://{ip_port}/login/'

# Create your views here.
class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'

class LogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'nagoyameshi/restaurant_list.html'

class UserCreatedView(TemplateView):
    template_name = 'user_created.html'
    
    # user_created.htmlに変数を書き出し
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_URL'] = f'http://{ip_port}/users/{UserActivateTokens.activate_token}/activation/'

class TopView(TemplateView):
    template_name = "top.html"
    model = Restaurant
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurants = Restaurant.objects.all()
        context['evaluated_restaurants'] = restaurants.order_by('-id')[:6]
        context['new_restaurants'] = restaurants.order_by('created_at')[:6]
        return context


class ListView(ListView):
    model = Restaurant
    
    def get_queryset(self):
        query = self.request.GET.get('query')

        if query:
            restaurants = Restaurant.objects.filter(
            Q(restaurant_name__icontains=query) | Q(address__icontains=query)
            )
        else:
            restaurants = Restaurant.objects.all()[:6]
        return restaurants
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.request.GET.get('title', '')
        return context

class SignupView(CreateView):
    form_class = SignUpForm
    model = User
    template_name = 'signup.html'
    # 登録成功時に移行
    success_url = reverse_lazy("usercreated")
    
class PasswordresetView(CreateView):
    form_class = PasswordresetForm
    model = User
    template_name = 'passwordreset.html'
    
def activate_user(request, activate_token):
    activated_user = UserActivateTokens.objects.activate_user_by_token(activate_token)
    if hasattr(activated_user, 'is_active'):
        if activated_user.is_active:
            message = f'本登録が完了しました！<br><a href={login_url}>ログインページ</a>'
        if not activated_user.is_active:
            message = '本登録に失敗しました。'
    if not hasattr(activated_user, 'is_active'):
        message = 'エラーが発生しました'
    return HttpResponse(message)