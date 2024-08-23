from django.contrib import admin
from .forms import RestaurantAdminForm
from .models import Restaurant, User, UserActivateTokens, Category, RegularHoliday, Terms, Review, Reservation, Company
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field


# Register your models here.
class RestaurantResource(resources.ModelResource):
   class Meta:
       model = Restaurant
       skip_unchanged = True
       use_bulk = True

class RestaurantAdmin(ImportExportModelAdmin):
    list_display = ('id', 'restaurant_name', 'postal_code', 'address',)
    search_fields = ('restaurant_name',)
    list_per_page = 25
    form = RestaurantAdminForm
    filter_horizontal = ('holiday', 'category_name',)
    resource_class = RestaurantResource

class UserResource(resources.ModelResource):
   class Meta:
       model = User
       skip_unchanged = True
       use_bulk = True
    
class UserAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'kana_name', 'email', 'is_staff',)
    search_fields = ('name', 'kana_name', 'email',)
    list_filter = ('is_staff',)
    list_per_page = 25
    resource_class = UserResource
    
class UserActivateTokensAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'user', 'activate_token', 'expired_at',)

class CategoryResource(resources.ModelResource):
   class Meta:
       model = Category
       skip_unchanged = True
       use_bulk = True

class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)
    resource_class = CategoryResource

class RegularHolidayAdmin(admin.ModelAdmin):
    list_display = ('holiday', 'holiday_index',)
    ordering = ('holiday_index',)
    
class TermsAdmin(admin.ModelAdmin):
    list_display = ('id',)

class ReviewResource(resources.ModelResource):
   class Meta:
       model = Review
       skip_unchanged = True
       use_bulk = True

class ReviewAdmin(ImportExportModelAdmin):
    list_display = ('restaurant_id', 'user_id',)
    #search_fields = ('restaurant_id',)
    resource_class = ReviewResource

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'reserved_date', 'reserved_time', 'number_of_people',)
    #search_fields = ('user', 'restaurant',)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'address', 'representative',)

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserActivateTokens, UserActivateTokensAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(RegularHoliday, RegularHolidayAdmin)
admin.site.register(Terms, TermsAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Company, CompanyAdmin)
