import environ
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from ..forms import UserUpdateForm
from ..mixins import OnlyMyUserInformationMixin, OnlyPayingMemberMixin
from ..models import Restaurant, User, Company, Terms, Category, Subscription

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

class TopView(TemplateView):
    template_name = "top.html"
    model = Restaurant, Category
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurants = Restaurant.objects.filter(is_active = True)
        all_categories = Category.objects.all()
        categories = [["和食", "washoku"], ["うどん", "udon"], ["丼物", "don"], ["ラーメン", "ramen"], ["おでん", "oden"], ["揚げ物", "fried"],]
        category_information = []
        for category in categories:
            url = (f'/media/{category[1]}.jpg')
            id = (all_categories.get(category_name = category[0]).pk)
            category_information.append({'name': category[0], 'url': url, 'id': id})
        context['user'] = self.request.user
        restaurants = restaurants.annotate(score = Avg("review__score"))
        context['evaluated_restaurants'] = restaurants.order_by('-score')[:6]
        context['new_restaurants'] = restaurants.order_by('-open_date')[:6]
        context['all_categories'] = all_categories.order_by('id')
        context['category_information'] = category_information
        return context


class UserView(OnlyMyUserInformationMixin, LoginRequiredMixin, DetailView):
    model = User
    template_name = "user.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_subscribed = False
        is_cancelled = False
        subscriptions = Subscription.objects.filter(user = user)
        if subscriptions.exists():
            for lapse_date in subscriptions.values_list("lapse_date", flat=True):
                if lapse_date == None:
                    is_subscribed = True
                    break
                elif lapse_date > date.today():
                    context["expired_date"] = lapse_date - relativedelta(days = 1)
                    is_subscribed = True
                    is_cancelled = True
                    break
        context["is_subscribed"] = is_subscribed
        context["is_cancelled"] = is_cancelled
        return context

class UserUpdateView(OnlyMyUserInformationMixin, UpdateView):
    form_class = UserUpdateForm
    model = User
    template_name = "user_update.html"

    def get_success_url(self):
        return reverse_lazy('user', kwargs=dict(pk = self.request.user.pk))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = self.request.user.pk
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return context

class SubscriptionView(OnlyPayingMemberMixin, TemplateView):
    template_name = "subscription.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_cancelled = False
        subscriptions = Subscription.objects.filter(user = user)
        for lapse_date in subscriptions.values_list("lapse_date", flat=True):
            if lapse_date == None:
                is_subscribed = True
                break
            elif lapse_date > date.today():
                context["expired_date"] = lapse_date - relativedelta(days = 1)
                is_subscribed = True
                is_cancelled = True
                break
        context["is_subscribed"] = is_subscribed
        context["is_cancelled"] = is_cancelled
        return context

class CompanyView(TemplateView):
    template_name = "company.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.get(id = 1)
        context['user_id'] = self.request.user.pk
        context["company"] = company
        return context

class TermsView(TemplateView):
    template_name = "terms.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms = Terms.objects.get(id = 1).content.replace('\\n', '\n')
        context['user_id'] = self.request.user.pk
        context["terms"] = terms
        return context

class TestView(View):
    template_name = "test.html"
