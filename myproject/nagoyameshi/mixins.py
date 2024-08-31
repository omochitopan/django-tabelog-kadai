from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Restaurant, Reservation, Review

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
        restaurants = Restaurant.objects.all()
        target_restaurant = []
        for restaurant in restaurants:
            for manager in restaurant.managers.all():
                if user == manager:
                    target_restaurant.append(restaurant)
                    break
        target_reservations = Reservation.objects.filter(restaurant__in=target_restaurant)
        target_user_id = []
        for reservation in target_reservations:
            target_user_id.append(reservation.user.pk)
        target_user_id = list(set(target_user_id))
        return user.role == 1 and user.pk == self.kwargs['user_id'] and self.kwargs['pk'] in target_user_id

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
