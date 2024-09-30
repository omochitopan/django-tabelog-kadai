import base64, datetime, environ, io
from datetime import date, time
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from ..forms import ReservationInputForm, RestaurantCreateForm, RestaurantEditForm, UserSearch, ReservedUserSearch, RestaurantSearch, CategoryCreateForm
from ..mixins import OnlyManagementUserMixin, OnlyManagedUserInformationMixin
from ..models import Restaurant, User, Reservation, Company, Terms, Category, RegularHoliday, ManagerRestaurantRelation
from ..utils.pagination import pagination

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

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
        if 'uploaded_image' in self.request.session:
            context['uploaded_image'] = self.request.session['uploaded_image']
            context['uploaded_image_data'] = self.request.session['uploaded_image_data']
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
        categories = "  ".join(categories)
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
        if 'image' in self.request.FILES:
            self.request.session['uploaded_image'] = self.request.FILES['image'].name
            self.request.session['uploaded_image_data'] = base64.b64encode(self.request.FILES['image'].read()).decode('utf-8')
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
        if 'uploaded_image' in self.request.session:
            image_name = self.request.session.get('uploaded_image')
            image_data = self.request.session.get('uploaded_image_data')
            image_file = InMemoryUploadedFile(
                io.BytesIO(base64.b64decode(image_data)),
                None,
                image_name,
                'image/jpeg',
                len(image_data),
                None,
            )
            qryset.image = image_file
        qryset.save()
        qryset.managers.add(self.request.user)
        if 'uploaded_image' in self.request.session:
            del self.request.session['uploaded_image']
            del self.request.session['uploaded_image_data']
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

    def form_valid(self, form):
        form.save() # 画像をアップロードする場合、フォームのFILESを含めて保存
        return super().form_valid(form)
    
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

class ManagementCategoryView(OnlyManagementUserMixin, ListView):
    model = Category
    template_name = "management/management_category.html"
    paginate_by = 15
    
    def get_queryset(self):
        if not hasattr(self, 'queryset') or self.queryset is None:
            self.queryset = super().get_queryset()
        if self.request.GET.get("query"):
            self.queryset = self.queryset.filter(category_name__icontains = self.request.GET.get("query"))
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
        if self.queryset:
            context['count'] = len(self.queryset)
        return context

class ManagementCategoryCreateView(OnlyManagementUserMixin, CreateView):
    form_class = CategoryCreateForm
    template_name = "management/management_category_create.html"
    
    def get_success_url(self):
        return reverse_lazy('managementcategory', kwargs=dict(user_id = self.request.user.pk))

class ManagementCategoryUpdateView(OnlyManagementUserMixin, UpdateView):
    model = Category
    form_class = CategoryCreateForm
    template_name = "management/management_category_update.html"
    
    def get_success_url(self):
        return reverse_lazy('managementcategory', kwargs=dict(user_id = self.request.user.pk))

class ManagementCategoryDeleteView(OnlyManagementUserMixin, DeleteView):
    model = Category
    template_name = "management/management_category_delete.html"
    
    def get_success_url(self):
        return reverse_lazy('managementcategory', kwargs=dict(user_id = self.request.user.pk))

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
