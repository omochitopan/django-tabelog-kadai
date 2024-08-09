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
    path('login/', views.LoginView.as_view(), name="login"),
    path('user_created', views.UserCreatedView.as_view(), name="usercreated"),
    path('passwordreset/', views.PasswordresetView.as_view(), name="passwordreset"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('', views.TopView.as_view(), name="top"),
    path('list/', views.ListView.as_view(), name='list'),
    path('category/', views.RestaurantCategoryList.as_view(), name='category'),
    path('detail/<int:pk>/', views.RestaurantDetailView.as_view(), name="detail"),
    path('users/<uuid:activate_token>/activation/', activate_user, name='users-activation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)