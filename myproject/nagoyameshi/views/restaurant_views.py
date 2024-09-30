import environ
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from ..models import Restaurant, Favorite, Category
from ..utils.pagination import pagination

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

class RestaurantSearchView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurant_search.html"
    paginate_by = 10
    
    def get_queryset(self):
        self.queryset = Restaurant.objects.filter(is_active = True).annotate(score = Avg("review__score"))
        keyword = self.request.GET.get('keyword')
        self.category = self.request.GET.get('category')
        price = self.request.GET.get('price')
        order = self.request.GET.get('order')
        if self.category == "0":
            self.category = None
        if keyword:
            self.queryset = self.queryset.filter(Q(restaurant_name__icontains = keyword) | Q(address__icontains = keyword))
        if self.category:
            self.queryset = self.queryset.filter(category_name = self.category)
        if price:
            if self.request.GET.get('minormax') == "min":
                if self.request.GET.get('upordown') == "down":
                    self.queryset = self.queryset.filter(lowest_price__lte = price)
                else:
                    self.queryset = self.queryset.filter(lowest_price__gte = price)
            else:
                if self.request.GET.get('upordown') == "down":
                    self.queryset = self.queryset.filter(highest_price__lte = price)
                else:
                    self.queryset = self.queryset.filter(highest_price__gte = price)
        if self.queryset:
            if order == "new":
                self.queryset = self.queryset.order_by("-open_date")
            elif order == "old":
                self.queryset = self.queryset.order_by("open_date")
            elif order == "mincheap":
                self.queryset = self.queryset.order_by("lowest_price")
            elif order == "minexpensive":
                self.queryset = self.queryset.order_by("-lowest_price")
            elif order == "highcheap":
                self.queryset = self.queryset.order_by("highest_price")
            elif order == "highexpensive":
                self.queryset = self.queryset.order_by("-highest_price")
            elif order == "scorelow":
                self.queryset = self.queryset.order_by("score")
            elif order == "scorehigh":
                self.queryset = self.queryset.order_by("-score")
        # Paginator
        paginator = Paginator(self.queryset, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            self.page_obj = paginator.page(page)
        except PageNotAnInteger:
            self.page_obj = paginator.page(1)
        except EmptyPage:
            self.page_obj = paginator.page(paginator.num_pages)
        # テンプレートに変数を渡す
        messages.add_message(self.request, messages.INFO, self.page_obj)
        return self.queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_page = self.page_obj
        current_num = current_page.number
        total_num = current_page.paginator.num_pages
        page_list = pagination(5, current_num, total_num)
        context['page_list'] = page_list
        context["price_list"] = [1000, 2000, 3000, 4000, 5000, 10000, 30000]
        if self.queryset:
            context['count'] = len(self.queryset)
        context["categories"] = Category.objects.all()
        if self.category:
            context["category"] = Category.objects.get(pk = self.category).category_name
        else:
            context["category"] = None
        return context

class RestaurantDetailView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = "restaurant_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        restaurant = get_object_or_404(Restaurant, pk = self.kwargs.get("pk"))
        isFavorite = Favorite.objects.filter(user = user, restaurant = restaurant).exists()
        context['user_id'] = user.pk
        context['isFavorite'] = isFavorite
        return context
