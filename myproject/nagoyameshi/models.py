from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission
from django.core.validators import RegexValidator, MinLengthValidator 
from django.conf import settings
import uuid
from datetime import datetime, timedelta
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
import environ
import os

env = environ.Env()
env_ip = env('ENV_IP')

class Restaurant(models.Model):
    PRICE_RANGES = (
        ('1', '¥0~999'),
        ('2', '¥1,000~1,999'),
        ('3', '¥2,000~2,999'),
        ('4', '¥3,000~3,999'),
        ('5', '¥4,000~4,999'),
        ('6', '¥5,000~9,999'),
        ('7', '¥10,000~30,000'),
        ('8', '¥30,000~')
    )
    
    name = models.CharField(verbose_name="店舗名", max_length=50)
    url = models.URLField(verbose_name="URL", blank=True, null=True)
    text = models.TextField(verbose_name="店舗説明", max_length=1000)
    address = models.CharField(verbose_name="店舗住所", max_length=200)
    price = models.CharField(verbose_name="価格帯", max_length=20, choices=PRICE_RANGES)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if extra_fields.get('is_staff') is not False:
            raise ValueError('User must have is_staff=False.')
        if extra_fields.get('is_superuser') is not False:
            raise ValueError('User must have is_superuser=False.')
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(verbose_name="お名前（漢字）", max_length=20)
    kana_name = models.CharField(verbose_name="お名前（フリガナ）", max_length=20)
    email = models.EmailField(verbose_name="e-mail", max_length=100, unique=True)
    # password_regex = RegexValidator(regex=r'^(?=.*[A-Z])(?=.*[.?/-])[a-zA-Z0-9.?/-]{8,24}$', 
    #                                 message = ("パスワードは半角8文字以上24文字以内で大文字と記号（.?/-）をそれぞれ1文字以上含めてください"))
    # password = models.CharField(verbose_name="パスワード", validators=[password_regex], max_length=256)
    postal_code_regex = RegexValidator(regex=r'^[0-9]{7}$', message = ("郵便番号は半角数字7文字で入力してください"))
    postal_code = models.CharField(verbose_name='郵便番号', validators=[postal_code_regex], max_length=7)
    address = models.CharField(verbose_name="住所", max_length=150)
    tel_number_regex = RegexValidator(regex=r'^[0-9]+$', message = ("電話番号は半角数字15文字以内で入力してください"))
    tel_number = models.CharField(verbose_name='電話番号', validators=[tel_number_regex], max_length=15)
    birthday = models.DateField(verbose_name="誕生日", blank=True, null=True)
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
        message = f'URLにアクセスして本登録を行なってください。\nhttp://{env_ip}/users/{user_activate_token.activate_token}/activation\nこのメールに心当たりが無い方はお手数ですが削除して頂くようお願い致します。'

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
