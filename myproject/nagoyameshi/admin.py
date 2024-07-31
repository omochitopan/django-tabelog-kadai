from django.contrib import admin
from .models import Restaurant, User, UserActivateTokens

# Register your models here.
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'kana_name', 'email', 'is_staff')
    search_fields = ('name', 'kana_name', 'email',)
    list_filter = ('is_staff',)
    list_per_page = 15
    
class UserActivateTokensAdmin(admin.ModelAdmin):
    list_display = ('token_id', 'user', 'activate_token', 'expired_at')

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserActivateTokens, UserActivateTokensAdmin)