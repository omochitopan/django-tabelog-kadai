import calendar, datetime, environ
from datetime import date
from dateutil.relativedelta import relativedelta
from django.views.generic.base import TemplateView
from ..mixins import OnlyAdministrationUserMixin
from ..models import Restaurant, User, Reservation, Subscription

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

class AdministrationUserView(OnlyAdministrationUserMixin, TemplateView):
    template_name = "administration/administration_user.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year_range = [year for year in (range(2020, date.today().year + 1) if date.today().month >= 4 else range(2020, date.today().year))]
        context["year_range"] = year_range
        context["month_range"] = [month for month in range(1, 13)]
        today = datetime.date.today()
        this_year = today.year
        this_month = today.month
        method = self.request.GET.get("method", "1")
        s_year = int(self.request.GET.get("s_year", this_year - 1))
        s_month = int(self.request.GET.get("s_month", (this_month + 1) if this_month < 12 else 1))
        e_year = int(self.request.GET.get("e_year", this_year))
        e_month = int(self.request.GET.get("e_month", this_month))
        context.update({
            "method": method,
            "s_year": s_year,
            "e_year": e_year,
            "s_month": s_month,
            "e_month": e_month,
        })
        # 月末で集計
        s_before = datetime.date(year = s_year, month = s_month, day=1)
        start = datetime.date(year = s_year, month = s_month, day = calendar.monthrange(s_year, s_month)[1])
        end = datetime.date(year = e_year, month = e_month, day = calendar.monthrange(e_year, e_month)[1])
        if end > today:
            end = datetime.date(year = this_year, month = this_month, day = calendar.monthrange(this_year, this_month)[1])
        if end >= start:
            months = []
            if method == "1":
                context["active_counts"] = self.calculate_active_users(start, end, months)
            elif method == "2":
                context["subscriber_counts"], context["free_counts"] = self.calculate_subscriber_free_users(start, end, months)
            elif method == "3":
                context["join_counts"], context["leave_counts"] = self.calculate_join_leave_users(start, end, months, s_before)
            context["months"] = months
        return context

    def calculate_active_users(self, start, end, months):
        active_counts = []
        while end >= start:
            total_users = User.objects.filter(registration_time__lte = start).count()
            resigned_users = User.objects.filter(resignation_time__lte = start).count()
            active_counts.append(total_users - resigned_users)
            months.append(int(f'{start.year}{start.month}'))
            start = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
        return active_counts

    def calculate_join_leave_users(self, start, end, months, s_before):
        join_counts, leave_counts = [], []
        while end >= start:
            join_users = User.objects.filter(registration_time__lte = start, registration_time__gte = s_before).count()
            leave_users = User.objects.filter(resignation_time__lte = start, resignation_time__gte = s_before).count()
            join_counts.append(join_users)
            leave_counts.append(leave_users)
            months.append(int(f'{start.year}{start.month}'))
            start = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
            s_before += relativedelta(months = 1)
        return join_counts, leave_counts

    def calculate_subscriber_free_users(self, start, end, months):
        subscriber_counts, free_counts = [], []
        while end >= start:
            total_users = User.objects.filter(registration_time__lte = start).count()
            resigned_users = User.objects.filter(resignation_time__lte = start).count()
            active_users = total_users - resigned_users
            subscribers = Subscription.objects.filter(registration_date__lte = start)
            subscribers = subscribers.filter(lapse_date__isnull = True).count() + subscribers.filter(lapse_date__gt = start).count()
            free_users = active_users - subscribers
            subscriber_counts.append(subscribers)
            free_counts.append(free_users)
            months.append(int(f'{start.year}{start.month}'))
            start = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
        return subscriber_counts, free_counts
    
class AdministrationRestaurantView(OnlyAdministrationUserMixin, TemplateView):
    template_name = "administration/administration_restaurant.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year_range = [year for year in (range(2020, date.today().year + 1) if date.today().month >= 4 else range(2020, date.today().year))]
        context["year_range"] = year_range
        context["month_range"] = [month for month in range(1, 13)]
        today = datetime.date.today()
        this_year = today.year
        this_month = today.month
        method = self.request.GET.get("method", "4")
        s_year = int(self.request.GET.get("s_year", this_year - 1))
        s_month = int(self.request.GET.get("s_month", (this_month + 1) if this_month < 12 else 1))
        e_year = int(self.request.GET.get("e_year", this_year))
        e_month = int(self.request.GET.get("e_month", this_month))
        context.update({
            "method": method,
            "s_year": s_year,
            "e_year": e_year,
            "s_month": s_month,
            "e_month": e_month,
        })
        # 月末で集計
        s_before = datetime.date(year = s_year, month = s_month, day = 1)
        start = datetime.date(year = s_year, month = s_month, day = calendar.monthrange(s_year, s_month)[1])
        end = datetime.date(year = e_year, month = e_month, day = calendar.monthrange(e_year, e_month)[1])
        if end > today:
            end = datetime.date(year = this_year, month = this_month, day = calendar.monthrange(this_year, this_month)[1])
        if end >= start:
            months = []
            if method == "4":
                context["open_counts"], context["closed_counts"] = self.calculate_open_closed_restaurants(start, end, months)
            elif method == "5":
                context["monthly_open_counts"], context["monthly_closed_counts"] = self.calculate_monthly_open_closed_restaurants(start, end, months, s_before)
            context["months"] = months
        return context

    def calculate_open_closed_restaurants(self, start, end, months):
        open_counts = []
        closed_counts = []
        while end >= start:
            restaurants = Restaurant.objects.filter(open_date__lte = start)
            open_restaurants_number = restaurants.filter(closed_date__isnull = True).count() + restaurants.filter(closed_date__gt = start).count()
            closed_restaurants_number = Restaurant.objects.filter(closed_date__lte = start).count()
            open_counts.append(open_restaurants_number)
            closed_counts.append(closed_restaurants_number)
            months.append(int(f'{start.year}{start.month}'))
            start = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
        return open_counts, closed_counts
    
    def calculate_monthly_open_closed_restaurants(self, start, end, months, s_before):
        monthly_open_counts, monthly_closed_counts = [], []
        while end >= start:
            open_restaurants = Restaurant.objects.filter(open_date__lte = start, open_date__gte = s_before).count()
            closed_restaurants = Restaurant.objects.filter(closed_date__lte = start, closed_date__gte = s_before).count()
            monthly_open_counts.append(open_restaurants)
            monthly_closed_counts.append(closed_restaurants)
            months.append(int(f'{start.year}{start.month}'))
            start = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
            s_before += relativedelta(months = 1)
        return monthly_open_counts, monthly_closed_counts

class AdministrationReservationView(OnlyAdministrationUserMixin, TemplateView):
    template_name = "administration/administration_reservation.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year_range = [year for year in (range(2020, date.today().year + 1) if date.today().month >= 4 else range(2020, date.today().year))]
        context["year_range"] = year_range
        context["month_range"] = [month for month in range(1, 13)]
        today = datetime.date.today()
        this_year = today.year
        this_month = today.month
        method = "6"
        restaurant_id = int(self.request.GET.get("restaurant", 0))
        s_year = int(self.request.GET.get("s_year", this_year - 1))
        s_month = int(self.request.GET.get("s_month", (this_month + 1) if this_month < 12 else 1))
        e_year = int(self.request.GET.get("e_year", this_year))
        e_month = int(self.request.GET.get("e_month", this_month))
        context.update({
            "restaurant_id": restaurant_id,
            "method": method,
            "s_year": s_year,
            "e_year": e_year,
            "s_month": s_month,
            "e_month": e_month,
        })
        # 月末で集計
        s_before = datetime.date(year = s_year, month = s_month, day=1)
        start = datetime.date(year = s_year, month = s_month, day = calendar.monthrange(s_year, s_month)[1])
        end = datetime.date(year = e_year, month = e_month, day = calendar.monthrange(e_year, e_month)[1])
        if end > today:
            end = datetime.date(year = this_year, month = this_month, day = calendar.monthrange(this_year, this_month)[1])
        if end >= start:
            months = []
            context["reservation_counts"] = self.calculate_reservations(restaurant_id, start, end, months, s_before)
            context["months"] = months
            context["restaurants"] = Restaurant.objects.all()
            if restaurant_id:
                context["restaurant_name"] = Restaurant.objects.get(pk = restaurant_id).restaurant_name
            else:
                context["restaurant_name"] = "全店舗"
        return context
    
    def calculate_reservations(self, restaurant_id, start, end, months, s_before):
        reservation_counts = []
        while end >= start:
            if not restaurant_id:
                reservations_number = Reservation.objects.filter(reserved_date__lte = start, reserved_date__gte = s_before).count()
            else:
                reservations_number = Reservation.objects.filter(restaurant__pk = self.request.GET.get("restaurant"), reserved_date__lte = start, reserved_date__gte = s_before).count()
            reservation_counts.append(reservations_number)
            months.append(int(f'{start.year}{start.month}'))
            start = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
            s_before += relativedelta(months = 1)
        return reservation_counts
    
class AdministrationSalesView(OnlyAdministrationUserMixin, TemplateView):
    template_name = "administration/administration_sales.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year_range = [year for year in (range(2020, date.today().year + 1) if date.today().month >= 4 else range(2020, date.today().year))]
        context["year_range"] = year_range
        context["month_range"] = [month for month in range(1, 13)]
        today = datetime.date.today()
        this_year = today.year
        this_month = today.month
        method = "7"
        s_year = int(self.request.GET.get("s_year", this_year - 1))
        s_month = int(self.request.GET.get("s_month", (this_month + 1) if this_month < 12 else 1))
        e_year = int(self.request.GET.get("e_year", this_year))
        e_month = int(self.request.GET.get("e_month", this_month))
        context.update({
            "method": method,
            "s_year": s_year,
            "e_year": e_year,
            "s_month": s_month,
            "e_month": e_month,
        })
        # 月末で集計
        start = datetime.date(year = s_year, month = s_month, day = calendar.monthrange(s_year, s_month)[1])
        s_after = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
        end = datetime.date(year = e_year, month = e_month, day = calendar.monthrange(e_year, e_month)[1])
        if end > today:
            end = datetime.date(year = this_year, month = this_month, day = calendar.monthrange(this_year, this_month)[1])
        if end >= start:
            months = []
            context["sales_counts"] = self.calculate_sales(start, end, months, s_after)
            context["months"] = months
        return context
    
    def calculate_sales(self, start, end, months, s_after):
        sales_counts = []
        while end >= start:
            sales = Subscription.objects.filter(registration_date__lte = start)
            sales_number = sales.filter(lapse_date__isnull = True).count() + sales.filter(lapse_date__gt = s_after).count()
            sales_counts.append(sales_number * 300)
            months.append(int(f'{start.year}{start.month}'))
            start = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
            s_after = datetime.date(start.year + (start.month == 12), (start.month % 12) + 1, calendar.monthrange(start.year + (start.month == 12), (start.month % 12) + 1)[1])
        return sales_counts
    