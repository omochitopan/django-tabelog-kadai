from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Reservation, Review, User, Subscription
from datetime import date

class OnlyManagementUserMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.role == 1 and user.pk == self.kwargs['user_id']

# 管理店舗を予約したことのあるユーザー情報以外の閲覧を制限
class OnlyManagedUserInformationMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        # 過去に予約したことのあるユーザーIDを取得
        user_ids = User.objects.filter(reservation__restaurant__managers=self.request.user).distinct().values_list("pk", flat=True)
        return (user.role == 1 and user.pk == self.kwargs['user_id'] and self.kwargs['pk'] in user_ids) or self.kwargs['pk'] == self.request.user.pk

class OnlyMyUserInformationMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.pk == self.kwargs.get("pk")

    """
    def test_func(self):
        user_id = self.request.user.pk
        if self.kwargs.get("pk"):
            return self.kwargs['pk'] == user_id
        else:
            return self.kwargs['user_id'] == user_id
    """

class OnlyMyReviewMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        review = Review.objects.get(pk = self.kwargs["pk"])
        return review.user.pk == self.request.user.pk

class OnlyMyReservationMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        reservation = Reservation.objects.get(pk = self.kwargs["pk"])
        return reservation.user.pk == self.request.user.pk

class OnlyPayingMemberMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        is_subscribed = False
        subscriptions = Subscription.objects.filter(user = self.request.user)
        for cancel_date in subscriptions.values_list("lapse_date", flat=True):
            if cancel_date == None or cancel_date >= date.today():
                is_subscribed = True
                break
        return is_subscribed

class OnlyAdministrationUserMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_superuser
