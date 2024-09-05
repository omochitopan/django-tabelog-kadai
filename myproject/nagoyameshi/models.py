from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from datetime import datetime, timedelta
import environ, uuid

env = environ.Env()
ip_port = env('IP_PORT')

postal_code_regex = RegexValidator(regex=r'^[0-9]{7}$', message = ("郵便番号は半角数字7文字で入力してください"))
tel_number_regex = RegexValidator(regex=r'^[0-9]+$', message = ("電話番号は半角数字15文字以内で入力してください"))
    
class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('e-mailは必須項目です')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 0)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if extra_fields.get('is_staff') is not False:
            raise ValueError('User must have is_staff=False.')
        if extra_fields.get('is_superuser') is not False:
            raise ValueError('User must have is_superuser=False.')
        return self._create_user(email, password, **extra_fields)

    def management_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 1)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if extra_fields.get('is_staff') is not False:
            raise ValueError('User must have is_staff=False.')
        if extra_fields.get('is_superuser') is not False:
            raise ValueError('User must have is_superuser=False.')
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('role', 1)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.IntegerChoices):
        GENERAL = 0
        MANAGEMENT = 1

    class Meta:
        db_table = 'nagoyameshi_user'
        verbose_name = verbose_name_plural = 'ユーザー'

    name = models.CharField(verbose_name="お名前（漢字）", max_length=50)
    kana_name = models.CharField(verbose_name="お名前（フリガナ）", max_length=50)
    nick_name = models.CharField(verbose_name="ニックネーム", max_length=50)
    email = models.EmailField(verbose_name="e-mail", max_length=100, unique=True)
    postal_code = models.CharField(verbose_name='郵便番号', validators=[postal_code_regex], max_length=7)
    address = models.CharField(verbose_name="住所", max_length=150)
    tel_number = models.CharField(verbose_name='電話番号', validators=[tel_number_regex], max_length=15)
    birthday = models.DateField(verbose_name="誕生日", blank=True, null=True)
    occupation = models.CharField(verbose_name='職業', max_length=20, blank=True, null=True)
    role = models.PositiveIntegerField(choices=Role.choices, default=Role.GENERAL)
    is_staff = models.BooleanField(verbose_name="スタッフ", default=False)
    is_superuser = models.BooleanField(verbose_name="スーパーユーザー", default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)
    
    objects = UserManager()
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    
class UserActivateTokensManager(models.Manager):
    def activate_user_by_token(self, activate_token):
        user_activate_token = self.filter(
            activate_token = activate_token,
            expired_at__gte = datetime.now() # __gte = greater than equal
        ).first()
        if hasattr(user_activate_token, 'user'):
            user = user_activate_token.user
            user.is_active = True
            user.save()
            return user

class UserActivateTokens(models.Model):
    class Meta:
        db_table = 'nagoyameshi_useractivatetokens'
        verbose_name = verbose_name_plural = 'メール認証トークン'
    
    token_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    activate_token = models.UUIDField(default=uuid.uuid4)
    expired_at = models.DateTimeField()

    objects = UserActivateTokensManager()
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def publish_activate_token(sender, instance, **kwargs):
    if not instance.is_active:
        user_activate_token = UserActivateTokens.objects.create(
            user=instance,
            expired_at=datetime.now()+timedelta(days=settings.ACTIVATION_EXPIRED_DAYS),
        )
        subject = 'Please Activate Your Account'
        message = f'URLにアクセスして本登録を行なってください。\nhttp://{ip_port}/users/{user_activate_token.activate_token}/activation\nこのメールに心当たりが無い方はお手数ですが削除して頂くようお願い致します。'

#    以下は本登録が完了した後にメールを送る設定だが、
#    ログイン時にもメールが送られてしまったため実装断念。
#    ログイン時にlast_login属性が更新されるため、
#    post_saveで拾ってしまっていることが原因か？
#    
#    if instance.is_active:
#        subject = 'Activated! Your Account!'
#        message = '本登録が完了しました！'

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [
            instance.email,
        ]
        send_mail(subject, message, from_email, recipient_list)

class RegularHoliday(models.Model):
    class Meta:
        db_table = 'nagoyameshi_regularholiday'
        verbose_name = verbose_name_plural = '定休日'
    
    holiday = models.CharField(verbose_name="定休日", max_length=3)
    holiday_index = models.PositiveIntegerField(verbose_name="定休日の番号", null=True)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return self.holiday

class Category(models.Model):
    class Meta:
        db_table = 'nagoyameshi_category'
        verbose_name = verbose_name_plural = 'カテゴリ'
    
    category_name = models.CharField(verbose_name="カテゴリ名", max_length=20)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return self.category_name

class Restaurant(models.Model):
    class Meta:
        db_table = 'nagoyameshi_restaurant'
        verbose_name = verbose_name_plural = 'レストラン'

    restaurant_name = models.CharField(verbose_name="店舗名", max_length=50)
    image = models.ImageField(verbose_name='店舗画像', default='noImage.png')
    description = models.TextField(verbose_name="説明", max_length=1000)
    lowest_price = models.PositiveIntegerField(verbose_name="最低価格", blank=True, null=True)
    highest_price = models.PositiveIntegerField(verbose_name="最高価格", blank=True, null=True)
    postal_code = models.CharField(verbose_name='郵便番号', validators=[postal_code_regex], max_length=7)
    address = models.CharField(verbose_name="店舗住所", max_length=200)
    opening_time = models.TimeField(verbose_name='開店時間')
    closing_time = models.TimeField(verbose_name='閉店時間')
    holiday = models.ManyToManyField(RegularHoliday, through="HolidayRestaurantRelation", verbose_name='定休日', blank=True)    
    seating_capacity = models.PositiveIntegerField(verbose_name='予約可能な座席数')
    category_name = models.ManyToManyField(Category, through="CategoryRestaurantRelation", verbose_name='カテゴリ（3つまで選択可）', blank=True)
    managers = models.ManyToManyField(User, through="ManagerRestaurantRelation", verbose_name="店舗管理ユーザー", blank=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return self.restaurant_name

class ManagerRestaurantRelation(models.Model):
    class Meta:
        db_table = 'nagoyameshi_managerrestaurantrelation'
        verbose_name = verbose_name_plural = '店舗運営者-レストラン'
        
    managers = models.ForeignKey("User", on_delete=models.CASCADE)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

class CategoryRestaurantRelation(models.Model):
    class Meta:
        db_table = 'nagoyameshi_categoryrestaurantrelation'
        verbose_name = verbose_name_plural = 'カテゴリ-レストラン'
    
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

class HolidayRestaurantRelation(models.Model):
    class Meta:
        db_table = 'nagoyameshi_holidayrestaurantrelation'
        verbose_name = verbose_name_plural = '定休日-レストラン'

    holiday = models.ForeignKey("RegularHoliday", on_delete=models.CASCADE)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

class Review(models.Model):
    class Meta:
        db_table = 'nagoyameshi_review'
        verbose_name = verbose_name_plural = 'レビュー'
    
    content = models.TextField(verbose_name="レビュー内容", max_length=1000)
    score = models.PositiveIntegerField(verbose_name="スコア", validators=[MinValueValidator(1), MaxValueValidator(5)])
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

class Reservation(models.Model):
    class Meta:
        db_table = 'nagoyameshi_reservation'
        verbose_name = verbose_name_plural = '予約'
    
    reserved_date = models.DateField(verbose_name="予約日")
    reserved_time = models.TimeField(verbose_name="予約時間")
    number_of_people = models.PositiveIntegerField(verbose_name="予約人数")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

class Favorite(models.Model):
    class Meta:
        db_table = 'nagoyameshi_favorite'
        verbose_name = verbose_name_plural = '予約'
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

class Company(models.Model):
    class Meta:
        db_table = 'nagoyameshi_company'
        verbose_name = verbose_name_plural = '会社概要'
    
    company_name = models.CharField(verbose_name="会社名", max_length=50)
    address = models.CharField(verbose_name="所在地", max_length=150)
    representative = models.CharField(verbose_name="代表者", max_length=50)
    establishment = models.DateField(verbose_name="設立")
    capital = models.CharField(verbose_name="資本金", max_length=50)
    business = models.CharField(verbose_name="事業内容", max_length=50)
    employee = models.CharField(verbose_name="従業員数", max_length=50)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

class Terms(models.Model):
    class Meta:
        db_table = "nagoyameshi_terms"
        verbose_name = verbose_name_plural = '利用規約'
    
    content = models.TextField(verbose_name="利用規約の本文")
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)
