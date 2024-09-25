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
    path('serviceguide/', views.ServiceGuideView.as_view(), name="serviceguide"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('usercreated', views.UserCreatedView.as_view(), name="usercreated"),
    path('passwordreset/', views.PasswordResetView.as_view(), name="password_reset"),
    path('passwordreset/done/', views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('passwordreset/confirm/<uidb64>/<token>//', views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('passwordreset/complete/', views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('passwordchange/', views.PasswordChange.as_view(), name='password_change'),
    path('passwordchange/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('signup/form/', views.SignupFormView.as_view(), name="signupform"),
    path('signup/confirm/', views.SignupConfirmView.as_view(), name="signupconfirm"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('upgrade/guide/', views.UpgradeGuideView.as_view(), name="upgradeguide"),
    path('upgrade/', views.create_checkout_session, name="checkoutsession"),
    path('stripe_webhooks/', views.webhook_received, name="webhook"),
    path('subscription/customerportal/', views.create_customer_portal_session, name="customerportal"),
    path('subscription/', views.SubscriptionView.as_view(), name="subscription"),
    path('success/', views.SuccessView.as_view(), name="success"),
    path('cancel/', views.CancelView.as_view(), name="cancel"),
    path('subscription/resign/confirm/', views.SubscriptionResignConfirmView.as_view(), name="subscriptionresignconfirm"),
    path('subscription/resign/', views.cancel_subscription, name="subscriptionresign"),
    path('subscription/resign/done/', views.SubscriptionResignDoneView.as_view(), name="subscriptionresigndone"),
    path('users/<uuid:activate_token>/activation/', views.activate_user, name='users-activation'),
    path('logout/', views.logout_view, name="logout"),
    path('resign/<int:pk>/', views.ResignView.as_view(), name="resign"),
    path('resign/done/', views.ResignDoneView.as_view(), name="resigndone"),
    path('restaurant/', views.RestaurantSearchView.as_view(), name='search'),
    path('restaurant/<int:pk>/detail/', views.RestaurantDetailView.as_view(), name="detail"),
    path('restaurant/<int:restaurant_id>/review/', views.ReviewListView.as_view(), name="reviewlist"),
    path('restaurant/<int:restaurant_id>/review/create/', views.ReviewCreateView.as_view(), name="reviewcreate"),
    path('restaurant/review/<int:pk>/update/', views.ReviewUpdateView.as_view(), name="reviewupdate"),
    path('restaurant/review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name="reviewdelete"),
    path('restaurant/<int:restaurant_id>/reservation/form/', views.ReservationFormView.as_view(), name="reservationform"),
    path('restaurant/<int:restaurant_id>/reservation/confirm/', views.ReservationConfirmView.as_view(), name="reservationconfirm"),
    path('restaurant/<int:restaurant_id>/reservation/create/', views.ReservationCreateView.as_view(), name="reservationcreate"),
    path('reservation/list/', views.ReservationListView.as_view(), name="reservationlist"),
    path('reservation/list/all/', views.ReservationListAllView.as_view(), name="reservationlistall"),
    path('reservation/delete/<int:pk>/', views.ReservationDeleteView.as_view(), name="reservationdelete"),
    path('favorite/create/<int:restaurant_id>/', views.FavoriteCreateView.as_view(), name="favoritecreate"),
    path('favorite/list/', views.FavoriteListView.as_view(), name="favoritelist"),
    path('favorite/delete/<int:restaurant_id>/', views.FavoriteDeleteView.as_view(), name="favoritedelete"),
    path('user/<int:pk>', views.UserView.as_view(), name="user"),
    path('user/<int:pk>/update', views.UserUpdateView.as_view(), name="userupdate"),
    path('company/', views.CompanyView.as_view(), name="company"),
    path('terms/', views.TermsView.as_view(), name="terms"),
    path('management/<int:user_id>/', views.ManagementTopView.as_view(), name="management"),
    path('management/<int:user_id>/restaurant/open/', views.ManagementOpenRestaurantView.as_view(), name="managementopenrestaurant"),
    path('management/<int:user_id>/restaurant/closed/', views.ManagementClosedRestaurantView.as_view(), name="managementclosedrestaurant"),
    path('management/<int:user_id>/restaurant/form/', views.ManagementRestaurantFormView.as_view(), name="managementrestaurantform"),
    path('management/<int:user_id>/restaurant/confirm/', views.ManagementRestaurantConfirmView.as_view(), name="managementrestaurantconfirm"),
    path('management/<int:user_id>/restaurant/create/', views.ManagementRestaurantCreateView.as_view(), name="managementrestaurantcreate"),
    path('management/<int:user_id>/restaurant/<int:pk>/', views.ManagementRestaurantDetailView.as_view(), name="managementrestaurantdetail"),
    path('management/<int:user_id>/restaurant/<int:pk>/edit/', views.ManagementRestaurantEditView.as_view(), name="managementrestaurantedit"),
    path('management/<int:user_id>/restaurant/<int:pk>/delete/', views.ManagementRestaurantDeleteView.as_view(), name="managementrestaurantdelete"),
    path('management/<int:user_id>/reservation/<int:restaurant_id>/', views.ManagementReservationRestaurantView.as_view(), name="managementreservationrestaurant"),
    path('management/<int:user_id>/reservation/<int:restaurant_id>/all/', views.ManagementReservationRestaurantAllView.as_view(), name="managementreservationrestaurantall"),
    path('management/<int:user_id>/reservation/<int:pk>/edit/', views.ManagementReservationEditView.as_view(), name="managementreservationedit"),
    path('management/<int:user_id>/reservation/<int:pk>/delete/', views.ManagementReservationDeleteView.as_view(), name="managementreservationdelete"),
    path('management/<int:user_id>/user_information/', views.ManagementUserView.as_view(), name="managementuser"),
    path('management/<int:user_id>/user_information/<int:pk>/', views.ManagementUserDetailView.as_view(), name="managementuserdetail"),
    path('management/<int:user_id>/manager_information/<int:pk>/', views.ManagementManagerDetailView.as_view(), name="managementmanagerdetail"),
    path('management/<int:user_id>/company/', views.ManagementCompanyView.as_view(), name="managementcompany"),
    path('management/<int:user_id>/terms/', views.ManagementTermsView.as_view(), name="managementterms"),
    path('administration/user/', views.AdministrationUserView.as_view(), name="administrationuser"),
    path('administration/restaurant/', views.AdministrationRestaurantView.as_view(), name="administrationrestaurant"),
    path('administration/reservation/', views.AdministrationReservationView.as_view(), name="administrationreservation"),
    path('administration/sales/', views.AdministrationSalesView.as_view(), name="administrationsales"),
    path('.well-known/acme-challenge/', views.TestView.as_view(), name="test"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)