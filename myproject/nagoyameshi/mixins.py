from django.contrib.auth.mixins import UserPassesTestMixin

class OnlyManagementUserMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.role == 1 and user.pk == self.kwargs['user_id']