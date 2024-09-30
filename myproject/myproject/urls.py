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
from nagoyameshi.views import administration_views, authentication_views, basic_views, favorite_views, management_views, reservation_views, restaurant_views, review_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', authentication_views.LoginView.as_view(), name="login"),
    path('logout/', authentication_views.logout_view, name="logout"),
    path('passwordreset/', authentication_views.PasswordResetView.as_view(), name="password_reset"),
    path('passwordreset/done/', authentication_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('passwordreset/confirm/<uidb64>/<token>//', authentication_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('passwordreset/complete/', authentication_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('passwordchange/', authentication_views.PasswordChange.as_view(), name='password_change'),
    path('passwordchange/done/', authentication_views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('signup/form/', authentication_views.SignupFormView.as_view(), name="signupform"),
    path('signup/confirm/', authentication_views.SignupConfirmView.as_view(), name="signupconfirm"),
    path('signup/', authentication_views.SignupView.as_view(), name="signup"),
    path('usercreated', authentication_views.UserCreatedView.as_view(), name="usercreated"),
    path('users/<uuid:activate_token>/activation/', authentication_views.activate_user, name='users-activation'),
    path('upgrade/guide/', authentication_views.UpgradeGuideView.as_view(), name="upgradeguide"),
    path('upgrade/', authentication_views.create_checkout_session, name="checkoutsession"),
    path('stripe_webhooks/', authentication_views.webhook_received, name="webhook"),
    path('subscription/customerportal/', authentication_views.create_customer_portal_session, name="customerportal"),
    path('subscription/', basic_views.SubscriptionView.as_view(), name="subscription"),
    path('success/', authentication_views.SuccessView.as_view(), name="success"),
    path('cancel/', authentication_views.CancelView.as_view(), name="cancel"),
    path('subscription/resign/confirm/', authentication_views.SubscriptionResignConfirmView.as_view(), name="subscriptionresignconfirm"),
    path('subscription/resign/', authentication_views.cancel_subscription, name="subscriptionresign"),
    path('subscription/resign/done/', authentication_views.SubscriptionResignDoneView.as_view(), name="subscriptionresigndone"),
    path('resign/<int:pk>/', authentication_views.ResignView.as_view(), name="resign"),
    path('resign/done/', authentication_views.ResignDoneView.as_view(), name="resigndone"),
    path('', basic_views.TopView.as_view(), name="top"),
    path('restaurant/', restaurant_views.RestaurantSearchView.as_view(), name='search'),
    path('restaurant/<int:pk>/detail/', restaurant_views.RestaurantDetailView.as_view(), name="detail"),
    path('restaurant/<int:restaurant_id>/review/', review_views.ReviewListView.as_view(), name="reviewlist"),
    path('restaurant/<int:restaurant_id>/review/create/', review_views.ReviewCreateView.as_view(), name="reviewcreate"),
    path('restaurant/review/<int:pk>/update/', review_views.ReviewUpdateView.as_view(), name="reviewupdate"),
    path('restaurant/review/<int:pk>/delete/', review_views.ReviewDeleteView.as_view(), name="reviewdelete"),
    path('restaurant/<int:restaurant_id>/reservation/form/', reservation_views.ReservationFormView.as_view(), name="reservationform"),
    path('restaurant/<int:restaurant_id>/reservation/confirm/', reservation_views.ReservationConfirmView.as_view(), name="reservationconfirm"),
    path('restaurant/<int:restaurant_id>/reservation/create/', reservation_views.ReservationCreateView.as_view(), name="reservationcreate"),
    path('reservation/delete/<int:pk>/', reservation_views.ReservationDeleteView.as_view(), name="reservationdelete"),
    path('reservation/list/', reservation_views.ReservationListView.as_view(), name="reservationlist"),
    path('reservation/list/all/', reservation_views.ReservationListAllView.as_view(), name="reservationlistall"),
    path('favorite/create/<int:restaurant_id>/', favorite_views.FavoriteCreateView.as_view(), name="favoritecreate"),
    path('favorite/delete/<int:restaurant_id>/', favorite_views.FavoriteDeleteView.as_view(), name="favoritedelete"),
    path('favorite/list/', favorite_views.FavoriteListView.as_view(), name="favoritelist"),
    path('user/<int:pk>', basic_views.UserView.as_view(), name="user"),
    path('user/<int:pk>/update', basic_views.UserUpdateView.as_view(), name="userupdate"),
    path('company/', basic_views.CompanyView.as_view(), name="company"),
    path('terms/', basic_views.TermsView.as_view(), name="terms"),
    path('management/<int:user_id>/', management_views.ManagementTopView.as_view(), name="management"),
    path('management/<int:user_id>/restaurant/open/', management_views.ManagementOpenRestaurantView.as_view(), name="managementopenrestaurant"),
    path('management/<int:user_id>/restaurant/closed/', management_views.ManagementClosedRestaurantView.as_view(), name="managementclosedrestaurant"),
    path('management/<int:user_id>/restaurant/form/', management_views.ManagementRestaurantFormView.as_view(), name="managementrestaurantform"),
    path('management/<int:user_id>/restaurant/confirm/', management_views.ManagementRestaurantConfirmView.as_view(), name="managementrestaurantconfirm"),
    path('management/<int:user_id>/restaurant/create/', management_views.ManagementRestaurantCreateView.as_view(), name="managementrestaurantcreate"),
    path('management/<int:user_id>/restaurant/<int:pk>/', management_views.ManagementRestaurantDetailView.as_view(), name="managementrestaurantdetail"),
    path('management/<int:user_id>/restaurant/<int:pk>/edit/', management_views.ManagementRestaurantEditView.as_view(), name="managementrestaurantedit"),
    path('management/<int:user_id>/restaurant/<int:pk>/delete/', management_views.ManagementRestaurantDeleteView.as_view(), name="managementrestaurantdelete"),
    path('management/<int:user_id>/category/', management_views.ManagementCategoryView.as_view(), name="managementcategory"),
    path('management/<int:user_id>/category/create/', management_views.ManagementCategoryCreateView.as_view(), name="managementcategorycreate"),
    path('management/<int:user_id>/category/<int:pk>/update/', management_views.ManagementCategoryUpdateView.as_view(), name="managementcategoryupdate"),
    path('management/<int:user_id>/category/<int:pk>/delete/', management_views.ManagementCategoryDeleteView.as_view(), name="managementcategorydelete"),
    path('management/<int:user_id>/reservation/<int:restaurant_id>/', management_views.ManagementReservationRestaurantView.as_view(), name="managementreservationrestaurant"),
    path('management/<int:user_id>/reservation/<int:restaurant_id>/all/', management_views.ManagementReservationRestaurantAllView.as_view(), name="managementreservationrestaurantall"),
    path('management/<int:user_id>/reservation/<int:pk>/edit/', management_views.ManagementReservationEditView.as_view(), name="managementreservationedit"),
    path('management/<int:user_id>/reservation/<int:pk>/delete/', management_views.ManagementReservationDeleteView.as_view(), name="managementreservationdelete"),
    path('management/<int:user_id>/user_information/', management_views.ManagementUserView.as_view(), name="managementuser"),
    path('management/<int:user_id>/user_information/<int:pk>/', management_views.ManagementUserDetailView.as_view(), name="managementuserdetail"),
    path('management/<int:user_id>/manager_information/<int:pk>/', management_views.ManagementManagerDetailView.as_view(), name="managementmanagerdetail"),
    path('management/<int:user_id>/company/', management_views.ManagementCompanyView.as_view(), name="managementcompany"),
    path('management/<int:user_id>/terms/', management_views.ManagementTermsView.as_view(), name="managementterms"),
    path('administration/user/', administration_views.AdministrationUserView.as_view(), name="administrationuser"),
    path('administration/restaurant/', administration_views.AdministrationRestaurantView.as_view(), name="administrationrestaurant"),
    path('administration/reservation/', administration_views.AdministrationReservationView.as_view(), name="administrationreservation"),
    path('administration/sales/', administration_views.AdministrationSalesView.as_view(), name="administrationsales"),
    path('.well-known/acme-challenge/', basic_views.TestView.as_view(), name="test"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)