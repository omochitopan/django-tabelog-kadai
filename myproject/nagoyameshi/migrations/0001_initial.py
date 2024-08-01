# Generated by Django 5.0.7 on 2024-08-01 16:21

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=20, verbose_name='カテゴリ名')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新日時')),
            ],
        ),
        migrations.CreateModel(
            name='RegularHoliday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('holiday', models.CharField(max_length=3, verbose_name='定休日')),
                ('holiday_index', models.PositiveIntegerField(null=True, verbose_name='定休日の番号')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新日時')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('name', models.CharField(max_length=20, verbose_name='お名前（漢字）')),
                ('kana_name', models.CharField(max_length=20, verbose_name='お名前（フリガナ）')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='e-mail')),
                ('postal_code', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='郵便番号は半角数字7文字で入力してください', regex='^[0-9]{7}$')], verbose_name='郵便番号')),
                ('address', models.CharField(max_length=150, verbose_name='住所')),
                ('tel_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='電話番号は半角数字15文字以内で入力してください', regex='^[0-9]+$')], verbose_name='電話番号')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='誕生日')),
                ('is_staff', models.BooleanField(default=False, verbose_name='スタッフ')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='スーパーユーザー')),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新日時')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_name', models.CharField(max_length=50, verbose_name='店舗名')),
                ('image', models.ImageField(default='noImage.png', upload_to='', verbose_name='店舗画像')),
                ('description', models.TextField(max_length=1000, verbose_name='説明')),
                ('lowest_price', models.PositiveIntegerField(blank=True, null=True, verbose_name='最低価格')),
                ('highest_price', models.PositiveIntegerField(blank=True, null=True, verbose_name='最高価格')),
                ('postal_code', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='郵便番号は半角数字7文字で入力してください', regex='^[0-9]{7}$')], verbose_name='郵便番号')),
                ('address', models.CharField(max_length=200, verbose_name='店舗住所')),
                ('opening_time', models.TimeField(verbose_name='開店時間')),
                ('closing_time', models.TimeField(verbose_name='閉店時間')),
                ('seating_capacity', models.PositiveIntegerField(verbose_name='予約可能な座席数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新日時')),
                ('holiday', models.ManyToManyField(blank=True, to='nagoyameshi.regularholiday', verbose_name='定休日')),
            ],
        ),
        migrations.CreateModel(
            name='UserActivateTokens',
            fields=[
                ('token_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('activate_token', models.UUIDField(default=uuid.uuid4)),
                ('expired_at', models.DateTimeField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
