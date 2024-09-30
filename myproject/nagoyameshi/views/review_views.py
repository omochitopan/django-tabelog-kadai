import datetime, environ
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from ..forms import ReviewForm
from ..mixins import OnlyMyReviewMixin
from ..models import Restaurant, Review, Subscription
from ..utils.pagination import pagination

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "review_list.html"
    paginate_by = 5
    
    def get_queryset(self):
        query = self.kwargs.get('restaurant_id')
        self.queryset = Review.objects.filter(restaurant = query).order_by('-updated_at')
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
        restaurant_id = self.kwargs.get("restaurant_id")
        average_score = self.queryset.aggregate(Avg('score'))['score__avg']
        if average_score == None:
            average_score = "---"
        else:
            average_score = "{:.2f}".format(average_score)
        try:
            writtenreview = self.queryset.get(user = self.request.user)
        except self.model.DoesNotExist:
            writtenreview = None
        context["page_list"] = page_list
        context["restaurant"] = Restaurant.objects.get(pk = restaurant_id)
        context["average_score"] = average_score
        context["writtenreview"] = writtenreview
        if self.queryset:
            context['count'] = len(self.queryset)
        is_subscribed = False
        subscriptions = Subscription.objects.filter(user = self.request.user)
        if subscriptions.exists():
            for lapse_date in subscriptions.values_list("lapse_date", flat=True):
                if lapse_date == None:
                    is_subscribed = True
                    break
                elif lapse_date > datetime.date.today():
                    is_subscribed = True
                    break
        context["is_subscribed"] = is_subscribed
        return context
    
class ReviewCreateView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    model = Review
    
    def get_success_url(self):
        return reverse_lazy('reviewlist', kwargs=dict(restaurant_id = self.kwargs.get("restaurant_id")))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        context["restaurant"] = Restaurant.objects.get(pk = self.kwargs.get("restaurant_id"))
        return context

    def form_valid(self, form):
        qryset = form.save(commit=False)
        qryset.user = self.request.user
        qryset.restaurant = Restaurant.objects.get(id = self.kwargs.get('restaurant_id'))
        qryset.save()
        return  super().form_valid(form)
    
class ReviewUpdateView(OnlyMyReviewMixin, LoginRequiredMixin, UpdateView):
    form_class = ReviewForm
    model = Review
    template_name = "review_update.html"
    
    def get_success_url(self):
        referer = self.request.session['HTTP_REFERER']
        return referer
    
    def get(self, request, *args, **kwargs):
        request.session["HTTP_REFERER"] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        context['referer'] = self.request.session["HTTP_REFERER"]
        return context

class ReviewDeleteView(OnlyMyReviewMixin, LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "review_delete.html"
    
    def get_success_url(self):
        review = Review.objects.get(pk = self.kwargs.get("pk"))
        return reverse_lazy('reviewlist', kwargs=dict(restaurant_id = review.restaurant.pk))

    def get(self, request, *args, **kwargs):
        request.session["HTTP_REFERER"] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        context["referer"] = self.request.session["HTTP_REFERER"]
        return context
