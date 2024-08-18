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
from nagoyameshi.views import activate_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.TopView.as_view(), name="top"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('usercreated', views.UserCreatedView.as_view(), name="usercreated"),
    path('passwordreset/', views.PasswordresetView.as_view(), name="passwordreset"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('users/<uuid:activate_token>/activation/', activate_user, name='users-activation'),
    path('logout/', views.logout_view, name="logout"),
    path('restaurant/', views.RestaurantListView.as_view(), name='list'),
    path('restaurant/category/', views.RestaurantCategoryList.as_view(), name='category'),
    path('restaurant/<int:pk>/detail/', views.RestaurantDetailView.as_view(), name="detail"),
    path('restaurant/<int:restaurant_id>/review/', views.ReviewListView.as_view(), name="reviewlist"),
    path('restaurant/<int:restaurant_id>/review/create/', views.ReviewCreateView.as_view(), name="reviewcreate"),
    path('restaurant/<int:restaurant_id>/review/<int:pk>/update/', views.ReviewUpdateView.as_view(), name="reviewupdate"),
    path('restaurant/<int:restaurant_id>/reservation/', views.ReservationCreateView.as_view(), name="reservationcreate"),
    path('restaurant/<int:user_id>/reservationlist/', views.ReservationListView.as_view(), name="reservationlist"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)