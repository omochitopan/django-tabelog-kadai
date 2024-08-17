from typing import Any, Dict
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import HttpResponse
from .models import Restaurant, User, UserActivateTokens, Category, Review
from .forms import SignUpForm, PasswordresetForm, ReviewForm
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
        return context

class TopView(TemplateView):
    template_name = "top.html"
    model = Restaurant, Category
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurants = Restaurant.objects.all()
        categories = Category.objects.all()
        context['evaluated_restaurants'] = restaurants.order_by('id')[:6]
        context['new_restaurants'] = restaurants.order_by('-created_at')[:6]
        context['categories'] = categories.order_by('id')
        return context

class RestaurantListView(ListView):
    model = Restaurant
    
    def get_queryset(self):
        query = self.request.GET.get('query')

        if query:
            restaurants = Restaurant.objects.filter(
            Q(restaurant_name__icontains=query) | Q(address__icontains=query) #| Q(category_name__in=query)
            )
        else:
            restaurants = Restaurant.objects.none()
        return restaurants

class RestaurantCategoryList(ListView):
    model = Restaurant
    template_name = "category_list.html"

    def get_queryset(self):
        query = self.request.GET.get('query')
        restaurants = Restaurant.objects.all()
        categoryRestaurants = []
        for restaurant in restaurants:
            for category in restaurant.category_name.all():
                if query == category.category_name:
                    categoryRestaurants.append(restaurant)
        return categoryRestaurants
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        restaurants = Restaurant.objects.all()
        categoryRestaurants = []
        for restaurant in restaurants:
            for category in restaurant.category_name.all():
                if query == category.category_name:
                    categoryRestaurants.append(restaurant)
                    break
        context["data"] = categoryRestaurants
        return context
    
class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "restaurant_detail.html"
    
    def get(self, request, *args, **kwargs):
        request.session["restaurant_id"] = self.get_object().pk
        request.session["restaurant_name"] = self.get_object().restaurant_name        
        return super().get(request, *args, **kwargs)

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

class ReviewListView(ListView):
    model = Review
    template_name = "review_list.html"
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.request.session["restaurant_id"]
        reviews = Review.objects
        target_reviews = reviews.filter(restaurant = restaurant_id)
        target_reviews = target_reviews.order_by('-updated_at')
        average_score = target_reviews.aggregate(Avg('score'))['score__avg']
        if average_score == None:
            average_score = "---"
        else:
            average_score = "{:.2f}".format(average_score)
        writtenreview = None
        for review in target_reviews:
            if review.user == self.request.user:
                writtenreview = review
                break
        context["restaurant_id"] = self.request.session["restaurant_id"]
        context["restaurant_name"] = self.request.session["restaurant_name"]
        context["target_reviews"] = target_reviews
        context["average_score"] = average_score
        context["writtenreview"] = writtenreview
        return context
    
class ReviewCreateView(CreateView):
    form_class = ReviewForm
    model = Review
    
    def get_success_url(self):
        restaurant_id = self.request.session["restaurant_id"]
        return reverse_lazy('reviewlist', kwargs=dict(restaurant_id = self.request.session['restaurant_id']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant_name"] = self.request.session["restaurant_name"]
        return context

    def form_valid(self, form):
        qryset = form.save(commit=False)
        qryset.user = self.request.user
        restaurant_id = self.request.session['restaurant_id']
        qryset.restaurant = Restaurant.objects.get(id = restaurant_id)
        qryset.save()
        return  super().form_valid(form)
    
class ReviewUpdateView(UpdateView):
    form_class = ReviewForm
    model = Review
    template_name = "review_update.html"
    
    def get_success_url(self):
        restaurant_id = self.request.session["restaurant_id"]
        return reverse_lazy('reviewlist', kwargs=dict(restaurant_id = self.request.session['restaurant_id']))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant_name"] = self.request.session["restaurant_name"]
        return context
