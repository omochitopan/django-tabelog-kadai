import datetime, environ
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http.response import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from ..models import Restaurant, Favorite, Subscription
from ..utils.pagination import pagination

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

class FavoriteCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs.get("restaurant_id"))
        favorite, created = Favorite.objects.get_or_create(user=user, restaurant=restaurant)

        if not created:
            favorite.delete()
            status = 'unfavorited'
        else:
            status = 'favorited'

        return JsonResponse({'status': 'success', 'favorite_status': status})

# favoritelistで解除ボタンを押した際のview    
class FavoriteDeleteView(LoginRequiredMixin, View): # LoginRequiredMixin,
    def post(self, request, *args, **kwargs):
        user = request.user
        restaurant_id = request.POST.get("button")
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        favorite = Favorite.objects.get(user=user, restaurant=restaurant)

        favorite.delete()
        
        return redirect('favoritelist')

class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = "favorite_list.html"
    paginate_by = 15
    
    def get_queryset(self):
        self.queryset = Favorite.objects.filter(user = self.request.user).order_by('-updated_at')
        paginator = Paginator(self.queryset, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            self.page_obj = paginator.page(page)
        except PageNotAnInteger:
            self.page_obj = paginator.page(1)
        except EmptyPage:
            self.page_obj = paginator.page(paginator.num_pages)
        messages.add_message(self.request, messages.INFO, self.page_obj)
        return self.queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_page = self.page_obj
        current_num = current_page.number
        total_num = current_page.paginator.num_pages
        page_list = pagination(5, current_num, total_num)
        user = self.request.user
        is_subscribed = False
        subscriptions = Subscription.objects.filter(user = user)
        if subscriptions.exists():
            for lapse_date in subscriptions.values_list("lapse_date", flat=True):
                if lapse_date == None:
                    is_subscribed = True
                    break
                elif lapse_date > datetime.date.today():
                    is_subscribed = True
                    break
        context["page_list"] = page_list
        context["is_subscribed"] = is_subscribed
        return context
