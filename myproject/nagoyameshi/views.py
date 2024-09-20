from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, FormView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from typing import Any, Dict
from .models import Restaurant, User, UserActivateTokens, Review, Reservation, Favorite, Company, Terms, Category, RegularHoliday, ManagerRestaurantRelation, Subscription
from .forms import SignUpForm, ReviewForm, ReservationInputForm, ReservationConfirmForm, UserUpdateForm, RestaurantCreateForm, RestaurantEditForm, UserSearch, ReservedUserSearch, RestaurantSearch
from .mixins import OnlyManagementUserMixin, OnlyManagedUserInformationMixin, OnlyMyUserInformationMixin, OnlyMyReviewMixin, OnlyMyReservationMixin
from .utils.pagination import pagination
from datetime import date, time
from dateutil.relativedelta import relativedelta
import datetime, environ, stripe

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

stripe.api_key = env("STRIPE_SECRET_KEY")

# Create your views here.
class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    
def logout_view(request):
    logout(request)
    return redirect('top')

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
        context['new_restaurants'] = restaurants.order_by('-created_at')[:6]
        context['all_categories'] = all_categories.order_by('id')
        context['category_information'] = category_information
        return context

class RestaurantSearchView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = "restaurant_search.html"
    paginate_by = 5
    
    def get_queryset(self):
        restaurants = Restaurant.objects.filter(is_active = True).annotate(score = Avg("review__score"))
        all_restaurants = self.request.GET.get('all')
        keyword = self.request.GET.get('keyword')
        self.category = self.request.GET.get('category')
        if self.category == "0":
            self.category = None
        if all_restaurants:
            self.queryset = restaurants.all()
        elif keyword or self.category:
            if keyword:
                self.queryset = restaurants.filter(Q(restaurant_name__icontains = keyword) | Q(address__icontains = keyword))
                if self.category:
                    self.queryset = self.queryset.filter(category_name = self.category)
            elif self.category:
                self.queryset = restaurants.filter(category_name = self.category)
        else:
            self.queryset = Restaurant.objects.none()
        if self.queryset:
            if self.request.GET.get("order") == "mincheap":
                self.queryset = self.queryset.order_by("lowest_price")
            elif self.request.GET.get("order") == "minexpensive":
                self.queryset = self.queryset.order_by("-lowest_price")
            elif self.request.GET.get("order") == "maxcheap":
                self.queryset = self.queryset.order_by("highest_price")
            elif self.request.GET.get("order") == "maxexpensive":
                self.queryset = self.queryset.order_by("-highest_price")
            elif self.request.GET.get("order") == "scorelow":
                self.queryset = self.queryset.order_by("score")
            elif self.request.GET.get("order") == "scorehigh":
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
        if self.queryset:
            context['count'] = len(self.queryset)
        context["categories"] = Category.objects.all()
        if self.category:
            context["category"] = Category.objects.get(pk = self.category).category_name
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

class ServiceGuideView(FormView):
    form_class = SignUpForm

class SignupFormView(FormView):
    form_class = SignUpForm
    template_name = "signup_form.html"
    
    def form_valid(self, form):
        context = {
            'form': form,
            'kwargs': self.kwargs,
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'signup_form.html', context)

class SignupConfirmView(FormView):
    form_class = SignUpForm
    
    def form_valid(self, form):
        passlength = len(form.cleaned_data.get("password1"))
        password = "･" * passlength
        context = {
            'form': form,
            'kwargs': self.kwargs,
            'password': password,
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'signup.html', context)
    
    def form_invalid(self, form):
        context = {
            'form': form,
            'kwargs': self.kwargs,
        }
        return render(self.request, 'signup_form.html', context)

class SignupView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('usercreated')

class SignupConfirmationView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("usercreated")

class PasswordReset(PasswordResetView):
    # パスワード変更URL付きメールのカスタマイズ
    subject_template_name = 'mail/subject.txt'
    email_template_name = "mail/message.txt"
    template_name = "password_reset.html"
    # パスワードリセット用URLの送信ページ
    success_url = reverse_lazy("passwordresetdone")

class PasswordResetDone(PasswordResetDoneView):
    # パスワード変更用URL送信完了ページ
    template_name = "password_reset_done.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["domain"] = ip_port
        #context["uuid_token"] = 
        return context

class PasswordResetConfirm(PasswordResetConfirmView):
    # 新パスワード入力用ページ
    success_url = reverse_lazy("passwordresetcomplete")
    template_name = "password_reset_confirm.html"


class PasswordResetComplete(PasswordResetCompleteView):
    # 新パスワード設定完了ページ
    template_name = "password_reset_complete.html"

class PasswordChange(PasswordChangeView):
    # パスワード変更ページ
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'password_change.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return context

class PasswordChangeDone(PasswordChangeDoneView):
    # パスワード変更完了ページ
    template_name = 'password_change_done.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        return context

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
        context['user'] = self.request.user
        context["restaurant"] = Restaurant.objects.get(pk = restaurant_id)
        context["average_score"] = average_score
        context["writtenreview"] = writtenreview
        if self.queryset:
            context['count'] = len(self.queryset)
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

class ReservationFormView(LoginRequiredMixin, FormView):
    form_class = ReservationInputForm
    template_name = "reservation_form.html"
    
    def get_form_kwargs(self):
        kwargs = super(ReservationFormView, self).get_form_kwargs()
        restaurant = Restaurant.objects.get(pk = self.kwargs.get('restaurant_id'))
        seating_capacity = restaurant.seating_capacity
        opening_time = restaurant.opening_time
        closing_time = restaurant.closing_time
        kwargs['request'] = self.request
        kwargs['seating_capacity'] = seating_capacity
        opening_time = datetime.datetime.combine(date.today(), opening_time)
        closing_time = datetime.datetime.combine(date.today(), closing_time)

        # 予約可能な開始時間:start_timeと終了時間:end_timeを設定
        # 閉店時間が24時を過ぎる場合の対応
        if opening_time > closing_time:
            closing_time = closing_time + relativedelta(days = +1)
        
        start_time = opening_time
        if 0 < start_time.minute < 30:
            start_time = start_time.replace(minute = 30)
        elif start_time.minute > 30:
            start_time += relativedelta(hours = +1)
            start_time = start_time.replace(minute = 0)
        
        end_time = closing_time + relativedelta(hours = -1)
        if 0 < end_time.minute < 30:
            end_time = end_time.replace(minute = 0)
        elif end_time.minute > 30:
            end_time = end_time.replace(minute = 30)
        
        reservation_candidates = []
        while start_time <= end_time:
            reservation_hour = start_time.hour
            reservation_minute = start_time.minute
            reservation_time = time(reservation_hour, reservation_minute)
            if reservation_time.minute == 0:
                writing_time = f"{reservation_hour}:0{reservation_minute}"
            else:
                writing_time = f"{reservation_hour}:{reservation_minute}"
            reservation_candidates.append((reservation_time, writing_time))
            start_time += relativedelta(minutes = +30)
        reservation_candidates = tuple(reservation_candidates)
        kwargs['reservation_candidates'] = reservation_candidates
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context["restaurant"] = Restaurant.objects.get(pk = self.kwargs.get("restaurant_id"))
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return context
    
    def form_valid(self, form):
        context = {
            'form': form,
            'restaurant': Restaurant.objects.get(pk = self.kwargs.get("restaurant_id")),
            'kwargs': self.kwargs,
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'reservation_form.html', context)

class ReservationConfirmView(LoginRequiredMixin, FormView):
    form_class = ReservationConfirmForm
    
    def form_valid(self, form):
        reserved_date = form.cleaned_data.get("reserved_date")
        week_days = ['月', '火', '水', '木', '金', '土', '日',]
        week_day = week_days[reserved_date.weekday()]
        context = {
            'form': form,
            'restaurant': Restaurant.objects.get(pk = self.kwargs.get("restaurant_id")),
            'kwargs': self.kwargs,
            'reserved_date': reserved_date,
            'week_day': week_day,
            'reserved_time': form.cleaned_data.get("reserved_time"),
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'reservation_create.html', context)
    
    def form_invalid(self, form):
        context = {
            'form': form,
            'restaurant': Restaurant.objects.get(pk = self.kwargs.get("restaurant_id")),
            'kwargs': self.kwargs,
        }
        return render(self.request, 'reservation_form.html', context)

class ReservationCreateView(LoginRequiredMixin, CreateView):
    form_class = ReservationConfirmForm
    success_url = reverse_lazy('reservationlist')
    
    def form_valid(self, form):
        qryset = form.save(commit=False)
        qryset.user = self.request.user
        qryset.restaurant = Restaurant.objects.get(id = self.kwargs.get('restaurant_id'))
        qryset.save()
        return  super().form_valid(form)
        
class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "reservation_list.html"
    paginate_by = 15
    
    def get_queryset(self):
        self.queryset = Reservation.objects.filter(user = self.request.user).filter(reserved_date__gte = date.today()).order_by('reserved_date', 'reserved_time')
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
        cancel_date = datetime.date.today() + relativedelta(days = 3)
        context["page_list"] = page_list
        context["cancel_date"] = cancel_date
        return context

class ReservationListAllView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "reservation_list_all.html"
    paginate_by = 15
    
    def get_queryset(self):
        self.queryset = Reservation.objects.filter(user = self.request.user).order_by('reserved_date', 'reserved_time')
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
        cancel_date = datetime.date.today() + relativedelta(days = 3)
        context["page_list"] = page_list
        context["cancel_date"] = cancel_date
        return context

class ReservationDeleteView(OnlyMyReservationMixin, LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = "reservation_delete.html"
    
    def get_success_url(self):
        return reverse_lazy('reservationlist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context["cancel_date"] = datetime.date.today() + relativedelta(days = 3)
        context["referer"] = self.request.META.get("HTTP_REFERER")
        return context

class FavoriteCreateView(LoginRequiredMixin, View): # LoginRequiredMixin,
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
        context["page_list"] = page_list
        return context

class UserView(OnlyMyUserInformationMixin, LoginRequiredMixin, DetailView):
    model = User
    template_name = "user.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = User.objects.get(pk = 1) # self.request.user
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

class UpgradeGuideView(LoginRequiredMixin, TemplateView):
    template_name = "upgrade_guide.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lookup_key"] = env("STRIPE_LOOKUP_KEY")
        return context

class SubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = "subscription.html"

def create_checkout_session(request):
    DOMAIN = ip_port
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id = request.user.pk,
            line_items=[
                {
                    'price': env("STRIPE_PRICE_ID"),
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url = DOMAIN + '/success/',
            cancel_url = DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def cancel_subscription(request):
    user = request.user
    subscription = Subscription.objects.filter(end_time = None).get(user__pk = user.pk)
    stripe_subscription_id = subscription.stripe_subscription_id
    try:
        stripe.Subscription.delete(stripe_subscription_id)

        # サブスクリプションステータスを更新
        user.is_subscribed = False
        user.save()
        subscription.end_time = datetime.datetime.now()
        subscription.save()

        # 解約完了ページにリダイレクト
        return redirect('subscription_cancelled')  # 'subscription_cancelled'は解約完了ページのURL名
    except stripe.error.StripeError as e:
        # Stripe APIでエラーが発生した場合
        return HttpResponse(f"Error cancelling subscription: {str(e)}", status=500)

@csrf_exempt
def webhook_received(request):
    endpoint_secret = env("STRIPE_WEBHOOK_SECRET")
    print(endpoint_secret)
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400) # Invalid payload
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400) # Invalid signature
    event_type = event['type']
    if event_type == 'checkout.session.completed':
        # チェックアウト成功時のアクション
        session = event['data']['object']
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')
        print(f"client_reference_id: {client_reference_id}")
        print(f"stripe_customer_id: {stripe_customer_id}")
        try:
            user = User.objects.get(pk = 1) # client_reference_id
            user.is_subscribed = True
            user.save()
            subscription = Subscription.objects.create(
                user = user,
                start_time = datetime.datetime.now(),
                stripe_customer_id = stripe_customer_id,
                stripe_subscription_id = stripe_subscription_id,
            )
            subscription.save()
        except Exception as e:
            return HttpResponse(f"Error creating profile: {str(e)}", status=500)
        print('支払いが完了しました！')
    elif event_type == 'customer.subscription.created':
        print('有料会員登録が開始されました。', event.id)
    elif event_type == 'customer.subscription.deleted':
        session = event['data']['object']
        client_reference_id = session.get('client_reference_id')
        stripe_subscription_id = session.get('subscription')
        user = User.objects.get(pk = client_reference_id)
        user.is_subscribed = False
        user.save()
        subscription = Subscription.objects.get(stripe_subscription_id = stripe_subscription_id)
        subscription.end_time = datetime.datetime.now()
        subscription.save()
        print('有料会員登録を解約しました。', event.id)
    return HttpResponse(status=200)

class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = "success.html"
    
class CancelView(LoginRequiredMixin, TemplateView):
    template_name = "cancel.html"
    
class SubscriptionResignConfirmView(LoginRequiredMixin, TemplateView):
    template_name = "subscription_resign_confirm.html"
    
class SubscriptionResignDoneView(LoginRequiredMixin, TemplateView):
    template_name = "subscription_resign_done.html"

class ResignView(OnlyMyUserInformationMixin, UpdateView):
    model = User
    template_name = "resign.html"
    success_url = reverse_lazy("resigndone")
    fields = ("is_active",)
    
    def update(request, pk):
        user = User.objects.get(pk = request.user.pk)
        user.is_active = False
        user.save()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        return context

class ResignDoneView(TemplateView):
    model = User
    template_name = "resign_done.html"

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

class ManagementTopView(OnlyManagementUserMixin, TemplateView):
    template_name = "management/management_top.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

class ManagementOpenRestaurantView(OnlyManagementUserMixin, ListView):
    model = ManagerRestaurantRelation
    template_name = "management/management_open_restaurant.html"
    paginate_by = 15

    def post(self, request, *args, **kwargs):
        request.session['restaurant_search'] = [self.request.POST.get('query', None),]
        return redirect("managementopenrestaurant", self.request.user.pk)    
    
    def get_queryset(self):
        self.queryset = ManagerRestaurantRelation.objects.filter(restaurant__is_active = True, managers = self.request.user)
        if 'restaurant_search' in self.request.session:
            form_value = self.request.session['restaurant_search']
            query = form_value[0]
            if query:
                self.queryset = self.queryset.filter(
                    Q(restaurant__restaurant_name__icontains = query) | Q(restaurant__postal_code = query) | Q(restaurant__address__icontains = query)
                )
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
        query = ''
        if 'restaurant_search' in self.request.session:
            form_value = self.request.session['restaurant_search']
            query = form_value[0]
        default_data = {'query': query,}
        form = RestaurantSearch(initial=default_data)
        current_page = self.page_obj
        current_num = current_page.number
        total_num = current_page.paginator.num_pages
        page_list = pagination(5, current_num, total_num)
        context["form"] = form
        context["page_list"] = page_list
        context["user"] = self.request.user
        return context

class ManagementClosedRestaurantView(OnlyManagementUserMixin, ListView):
    model = Restaurant
    template_name = "management/management_closed_restaurant.html"
    paginate_by = 15
    
    def post(self, request, *args, **kwargs):
        request.session['restaurant_search'] = [self.request.POST.get('query', None),]
        return redirect("managementclosedrestaurant", self.request.user.pk)    
    
    def get_queryset(self):
        self.queryset = ManagerRestaurantRelation.objects.filter(restaurant__is_active = False, managers = self.request.user)
        if 'restaurant_search' in self.request.session:
            form_value = self.request.session['restaurant_search']
            query = form_value[0]
            if query:
                self.queryset = self.queryset.filter(
                    Q(restaurant__restaurant_name__icontains = query) | Q(restaurant__postal_code = query) | Q(restaurant__address__icontains = query)
                )
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
        query = ''
        if 'restaurant_search' in self.request.session:
            form_value = self.request.session['restaurant_search']
            query = form_value[0]
        default_data = {'query': query,}
        form = RestaurantSearch(initial=default_data)
        current_page = self.page_obj
        current_num = current_page.number
        total_num = current_page.paginator.num_pages
        page_list = pagination(5, current_num, total_num)
        context["form"] = form
        context["page_list"] = page_list
        context["user"] = self.request.user
        return context

class ManagementRestaurantFormView(OnlyManagementUserMixin, FormView):
    form_class = RestaurantCreateForm
    template_name = "management/management_restaurant_form.html"

    def form_valid(self, form):
        context = {
            'form': form,
            'kwargs': self.kwargs,
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'management/management_restaurant_form.html', context)
    
class ManagementRestaurantConfirmView(OnlyManagementUserMixin, FormView):
    form_class = RestaurantCreateForm

    def form_valid(self, form):
        holiday_indices = [int(i) for i in form.cleaned_data.get("holiday")]
        holidays = []
        for i in holiday_indices:
            holidays.append(RegularHoliday.objects.get(holiday_index = i).holiday)
        holidays = " ".join(holidays)
        category_indices = [int(i) for i in form.cleaned_data.get("category_name")]
        categories = []
        description = form.cleaned_data.get("description").rstrip('\r\n')
        for i in category_indices:
            categories.append(Category.objects.get(pk = i).category_name)
        categories = "　".join(categories)
        context = {
            'form': form,
            'kwargs': self.kwargs,
            'description': description,
            'opening_time': form.cleaned_data.get("opening_time"),
            'closing_time': form.cleaned_data.get("closing_time"),
            'holidays': holidays,
            'categories': categories,
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'management/management_restaurant_create.html', context)
    
    def form_invalid(self, form):
        context = {
            'form': form,
            'kwargs': self.kwargs,
        }
        return render(self.request, 'management/management_restaurant_form.html', context)

class ManagementRestaurantCreateView(OnlyManagementUserMixin, CreateView):
    form_class = RestaurantCreateForm

    def get_success_url(self):
        return reverse_lazy('managementopenrestaurant', kwargs=dict(user_id = self.request.user.pk))

    def form_valid(self, form):
        qryset = form.save(commit=False)
        qryset.save()
        qryset.managers.add(self.request.user)
        return  super().form_valid(form)

class ManagementRestaurantDetailView(OnlyManagementUserMixin, DetailView):
    model = Restaurant
    template_name = "management/management_restaurant_detail.html"
    
    def get(self, request, *args, **kwargs):
        if "open" in self.request.META.get("HTTP_REFERER") or "closed" in self.request.META.get("HTTP_REFERER"):
            self.request.session["HTTP_REFERER"] = self.request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        context['referer'] = self.request.session["HTTP_REFERER"]
        return context

class ManagementRestaurantEditView(OnlyManagementUserMixin, UpdateView):
    form_class = RestaurantEditForm
    model = Restaurant
    template_name = "management/management_restaurant_edit.html"
    
    def get_success_url(self):
        restaurant_id = self.kwargs["pk"]
        return reverse_lazy('managementrestaurantdetail', kwargs=dict(user_id = self.request.user.pk, pk = restaurant_id))

    #forms.pyに値を渡す
    def get_form_kwargs(self): 
        kwargs = super(ManagementRestaurantEditView, self).get_form_kwargs()
        restaurant = Restaurant.objects.get(pk = self.kwargs.get("pk"))
        holidays = [holiday["id"] for holiday in restaurant.holiday.values()]
        categories = [category["id"] for category in restaurant.category_name.values()]
        kwargs['holidays'] = holidays
        kwargs['categories'] = categories
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return context

class ManagementRestaurantDeleteView(OnlyManagementUserMixin, UpdateView):
    model = Restaurant
    template_name = "management/management_restaurant_delete.html"
    fields = ("is_active",)
    
    def get_success_url(self):
        return reverse_lazy('managementopenrestaurant', kwargs=dict(user_id = self.request.user.pk))
    
    def update(request, pk):
        restaurant = Restaurant.objects.get(pk = request.kwargs["pk"])
        restaurant.is_active = False
        restaurant.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

class ManagementReservationRestaurantView(OnlyManagementUserMixin, ListView):
    model = Reservation
    template_name = "management/management_reservation_restaurant.html"
    paginate_by = 15
    
    def post(self, request, *args, **kwargs):
        request.session['reserved_user_search'] = [self.request.POST.get('query', None),]
        return redirect("managementreservationrestaurant", self.request.user.pk, self.kwargs.get("restaurant_id"))    
    
    def get_queryset(self):
        target_restaurant = Restaurant.objects.get(pk = self.kwargs.get("restaurant_id"))
        self.queryset = Reservation.objects.filter(restaurant = target_restaurant, reserved_date__gte = date.today()).order_by("reserved_date", "reserved_time")
        if 'reserved_user_search' in self.request.session:
            form_value = self.request.session['reserved_user_search']
            query = form_value[0]
            if query:
                query = query.replace("-", "")
                self.queryset = self.queryset.filter(
                    Q(user__name__icontains = query) | Q(user__kana_name__icontains = query) | Q(user__tel_number = query)
                )
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
        query = ''
        if 'reserved_user_search' in self.request.session:
            form_value = self.request.session['reserved_user_search']
            query = form_value[0]
        default_data = {'query': query,}
        form = ReservedUserSearch(initial=default_data)
        current_page = self.page_obj
        current_num = current_page.number
        total_num = current_page.paginator.num_pages
        page_list = pagination(5, current_num, total_num)
        restaurant_id = self.kwargs.get("restaurant_id")
        target_restaurant = Restaurant.objects.get(pk = restaurant_id)
        context['form'] = form
        context["page_list"] = page_list
        context["restaurant_id"] = restaurant_id
        context['target_restaurant'] = target_restaurant
        return context
    
class ManagementReservationRestaurantAllView(OnlyManagementUserMixin, ListView):
    model = Reservation
    template_name = "management/management_reservation_restaurant_all.html"
    paginate_by = 15

    def post(self, request, *args, **kwargs):
        request.session['reserved_user_search'] = [self.request.POST.get('query', None),]
        return redirect("managementreservationrestaurantall", self.request.user.pk, self.kwargs.get("restaurant_id"))    
    
    def get_queryset(self):
        target_restaurant = Restaurant.objects.get(pk = self.kwargs.get("restaurant_id"))
        self.queryset = Reservation.objects.filter(restaurant = target_restaurant).order_by("reserved_date", "reserved_time")
        if 'reserved_user_search' in self.request.session:
            form_value = self.request.session['reserved_user_search']
            query = form_value[0]
            if query:
                query = query.replace("-", "")
                self.queryset = self.queryset.filter(
                    Q(user__name__icontains = query) | Q(user__kana_name__icontains = query) | Q(user__tel_number = query)
                )
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
        query = ''
        if 'reserved_user_search' in self.request.session:
            form_value = self.request.session['reserved_user_search']
            query = form_value[0]
        default_data = {'query': query,}
        form = ReservedUserSearch(initial=default_data)
        current_page = self.page_obj
        current_num = current_page.number
        total_num = current_page.paginator.num_pages
        page_list = pagination(5, current_num, total_num)
        restaurant_id = self.kwargs.get("restaurant_id")
        target_restaurant = Restaurant.objects.get(pk = restaurant_id)
        context['form'] = form
        context["page_list"] = page_list
        context["restaurant_id"] = restaurant_id
        context['target_restaurant'] = target_restaurant
        context["today"] = date.today()
        return context

class ManagementReservationEditView(OnlyManagementUserMixin, UpdateView):
    form_class = ReservationInputForm
    model = Reservation
    template_name = "management/management_reservation_edit.html"
    
    def get_success_url(self):
        return self.request.session['HTTP_REFERER']
    
    def get(self, request, *args, **kwargs):
        request.session["HTTP_REFERER"] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super(ManagementReservationEditView, self).get_form_kwargs()
        reservation_id = self.kwargs.get('pk')
        restaurant = Reservation.objects.get(pk = reservation_id).restaurant
        seating_capacity = restaurant.seating_capacity
        opening_time = restaurant.opening_time
        closing_time = restaurant.closing_time
        kwargs['request'] = self.request
        kwargs['seating_capacity'] = seating_capacity
        opening_time = datetime.datetime.combine(date.today(), opening_time)
        closing_time = datetime.datetime.combine(date.today(), closing_time)

        if opening_time > closing_time:
            closing_time = closing_time + relativedelta(days = +1)
        
        start_time = opening_time
        if 0 < start_time.minute < 30:
            start_time = start_time.replace(minute = 30)
        elif start_time.minute > 30:
            start_time += relativedelta(hours = +1)
            start_time = start_time.replace(minute = 0)
        
        end_time = closing_time + relativedelta(hours = -1)
        if 0 < end_time.minute < 30:
            end_time = end_time.replace(minute = 0)
        elif end_time.minute > 30:
            end_time = end_time.replace(minute = 30)
        
        reservation_candidates = []
        while start_time <= end_time:
            reservation_hour = start_time.hour
            reservation_minute = start_time.minute
            reservation_time = time(reservation_hour, reservation_minute)
            if reservation_time.minute == 0:
                writing_time = f"{reservation_hour}:0{reservation_minute}"
            else:
                writing_time = f"{reservation_hour}:{reservation_minute}"
            reservation_candidates.append((reservation_time, writing_time))
            start_time += relativedelta(minutes = +30)
        reservation_candidates = tuple(reservation_candidates)
        kwargs['reservation_candidates'] = reservation_candidates
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["referer"] = self.request.META.get('HTTP_REFERER')
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return context

class ManagementReservationDeleteView(OnlyManagementUserMixin, DeleteView):
    model = Reservation
    template_name = "management/management_reservation_delete.html"
    
    def get_success_url(self):
        restaurant_id = Reservation.objects.get(pk = self.kwargs.get("pk")).restaurant.pk
        return reverse_lazy("managementreservationrestaurant", kwargs=dict(user_id = self.request.user.pk, restaurant_id = restaurant_id))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context["referer"] = self.request.META.get('HTTP_REFERER')
        return context

class ManagementUserView(OnlyManagementUserMixin, ListView):
    model = User
    template_name = "management/management_user.html"
    paginate_by = 15

    def post(self, request, *args, **kwargs):
        form_value = [
            self.request.POST.get('name', None),
            self.request.POST.get('email', None),
            self.request.POST.get('tel', None),
            self.request.POST.get('address', None),
            self.request.POST.get('status', None),
        ]
        request.session['form_value'] = form_value
        return redirect("managementuser", self.request.user.pk)
    
    def get_queryset(self):
        self.queryset = User.objects.filter(reservation__restaurant__managers=self.request.user).distinct()
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            name = form_value[0]
            email = form_value[1]
            tel = form_value[2]
            address = form_value[3]
            status = form_value[4]
            if name:
                self.queryset = self.queryset.filter(
                    Q(name__icontains = name) | Q(kana_name__icontains = name)
                )
            if email:
                self.queryset = self.queryset.filter(email__icontains = email)
            if tel:
                self.queryset = self.queryset.filter(tel_number = tel.replace("-", ""))
            if address:
                self.queryset = self.queryset.filter(is_active = True).filter(Q(postal_code = address) | Q(address__icontains = address))
            if status == "1":
                self.queryset = self.queryset.filter(is_active = True)
            elif status == "2":
                self.queryset = self.queryset.filter(is_active = False)
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
        name = ''
        email = ''
        tel = ''
        address = ''
        status = ''
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            name = form_value[0]
            email = form_value[1]
            tel = form_value[2]
            address = form_value[3]
            status = form_value[4]
        default_data = {'name': name,
                        'email': email,
                        'tel': tel,
                        'address': address,
                        'status': status,
                        }
        form = UserSearch(initial=default_data)
        current_page = self.page_obj
        current_num = current_page.number
        total_num = current_page.paginator.num_pages
        page_list = pagination(5, current_num, total_num)
        context['form'] = form
        context["page_list"] = page_list
        context["user"] = self.request.user
        return context

class ManagementUserDetailView(OnlyManagedUserInformationMixin, DetailView):
    model = User
    template_name = "management/management_user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

class ManagementManagerDetailView(OnlyManagementUserMixin, DetailView):
    model = User
    template_name = "management/management_manager_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

class ManagementCompanyView(TemplateView):
    template_name = "management/management_company.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.get(id = 1)
        context["user"] = self.request.user
        context["company"] = company
        return context

class ManagementTermsView(TemplateView):
    template_name = "management/management_terms.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms = Terms.objects.get(id = 1).content.replace('\\n', '\n')
        context["user"] = self.request.user
        context["terms"] = terms
        return context

class TestView(View):
    template_name = "test.html"
