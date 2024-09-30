import datetime, environ
from datetime import date, time
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.views.generic.edit import CreateView, DeleteView
from ..forms import ReservationInputForm, ReservationConfirmForm
from ..mixins import OnlyMyReservationMixin
from ..models import Restaurant, Reservation, Subscription
from ..utils.pagination import pagination

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

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
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return context
    
    def form_valid(self, form):
        context = {
            'form': form,
            'restaurant': Restaurant.objects.get(pk = self.kwargs.get("restaurant_id")),
            'kwargs': self.kwargs,
            'is_subscribed': True
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context["is_subscribed"] = is_subscribed
        return context
        
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
        cancel_limit = datetime.date.today() + relativedelta(days = 3)
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
        context["cancel_limit"] = cancel_limit
        context["is_subscribed"] = is_subscribed
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
        cancel_limit = datetime.date.today() + relativedelta(days = 3)
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
        context["cancel_limit"] = cancel_limit
        context["is_subscribed"] = is_subscribed
        return context

class ReservationDeleteView(OnlyMyReservationMixin, DeleteView):
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
