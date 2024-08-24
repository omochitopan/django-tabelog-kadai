"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from nagoyameshi import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.TopView.as_view(), name="top"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('usercreated', views.UserCreatedView.as_view(), name="usercreated"),
    path('passwordreset/', views.PasswordResetView.as_view(), name="password_reset"),
    path('passwordreset/done/', views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('passwordreset/confirm/<uidb64>/<token>//', views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('passwordreset/complete/', views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('users/<uuid:activate_token>/activation/', views.activate_user, name='users-activation'),
    path('logout/', views.logout_view, name="logout"),
    path('restaurant/', views.RestaurantListView.as_view(), name='list'),
    path('restaurant/category/', views.RestaurantCategoryList.as_view(), name='category'),
    path('restaurant/<int:pk>/detail/', views.RestaurantDetailView.as_view(), name="detail"),
    path('restaurant/<int:restaurant_id>/review/', views.ReviewListView.as_view(), name="reviewlist"),
    path('restaurant/<int:restaurant_id>/review/create/', views.ReviewCreateView.as_view(), name="reviewcreate"),
    path('restaurant/<int:restaurant_id>/review/<int:pk>/update/', views.ReviewUpdateView.as_view(), name="reviewupdate"),
    path('restaurant/<int:restaurant_id>/review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name="reviewdelete"),
    path('restaurant/<int:restaurant_id>/reservation/', views.ReservationCreateView.as_view(), name="reservationcreate"),
    path('restaurant/<int:user_id>/reservationlist/', views.ReservationListView.as_view(), name="reservationlist"),
    path('restaurant/<int:user_id>/reservationlist/all/', views.ReservationListAllView.as_view(), name="reservationlistall"),
    path('restaurant/<int:user_id>/reservationdelete/<int:pk>/', views.ReservationDeleteView.as_view(), name="reservationdelete"),
    path('favorite/create/<int:restaurant_id>/', views.FavoriteCreateView.as_view(), name="favoritecreate"),
    path('favorite/list/<int:user_id>/', views.FavoriteListView.as_view(), name="favoritelist"),
    path('favorite/delete/<int:restaurant_id>/', views.FavoriteDeleteView.as_view(), name="favoritedelete"),
    path('user/<int:pk>', views.UserView.as_view(), name="user"),
    path('user/<int:pk>/update', views.UserUpdateView.as_view(), name="userupdate"),
    path('company/', views.CompanyView.as_view(), name="company"),
    path('terms/', views.TermsView.as_view(), name="terms"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)