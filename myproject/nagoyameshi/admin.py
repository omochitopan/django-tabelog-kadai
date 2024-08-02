from django.contrib import admin
#from .forms import RestaurantAdminForm
from .models import Restaurant, User, UserActivateTokens, Category, RegularHoliday

# Register your models here.
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant_name', 'postal_code', 'address')
    search_fields = ('restaurant_name',)
    list_per_page = 15
#    form = RestaurantAdminForm
    
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'kana_name', 'email', 'is_staff')
    search_fields = ('name', 'kana_name', 'email',)
    list_filter = ('is_staff',)
    list_per_page = 15
    
class UserActivateTokensAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'user', 'activate_token', 'expired_at')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)

class RegularHolidayAdmin(admin.ModelAdmin):
    list_display = ('holiday', 'holiday_index',)

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserActivateTokens, UserActivateTokensAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(RegularHoliday, RegularHolidayAdmin)
