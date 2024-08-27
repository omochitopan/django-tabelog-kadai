from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Review, Reservation, Restaurant, RegularHoliday, Category
from dateutil.relativedelta import relativedelta
import datetime

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder':'名古屋 太郎',})
        self.fields['kana_name'].widget.attrs.update({'placeholder':'ナゴヤ タロウ',})
        self.fields['email'].widget.attrs.update({'placeholder': 'tarou@nagoyameshi.com',})
        self.fields['postal_code'].widget.attrs.update({'placeholder': '0123456',})
        self.fields['address'].widget.attrs.update({'placeholder': '愛知県栄区X-X-X',})
        self.fields['tel_number'].widget.attrs.update({'placeholder': '09012345678',})
    
    email = forms.EmailField(label = "メールアドレス")

    class Meta:
        model = User
        fields = (
            "name",
            "kana_name",
            "email",
            "postal_code",
            "address",
            "tel_number",
            "birthday",
            "occupation",
        )
        this_year = datetime.date.today().year
        widgets = {
            "birthday": forms.SelectDateWidget(
                years=range(this_year - 120, this_year),
            ),
        }

class PasswordresetForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
        )
        
class RestaurantAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('category_name') == None:
            cleaned_data.get('category_name') == []
        elif len(cleaned_data.get('category_name')) > 3:
            raise ValidationError('カテゴリは3つまで選択可能です')
        
    #以下はチェックボックススタイル適用
    #holiday = forms.MultipleChoiceField(
    #    choices = RegularHoliday.objects.values_list('holiday', 'holiday').distinct(),
    #    label = '定休日',
    #    widget = forms.CheckboxSelectMultiple,
    #    required = False,
    #    )
    
    #category_name = forms.MultipleChoiceField(
    #    choices = Category.objects.values_list('category_name', 'category_name').distinct(),
    #    label = 'カテゴリ（3つまで選択可）',
    #    widget = forms.CheckboxSelectMultiple,
    #    required = False,
    #    )

class ReviewForm(forms.ModelForm):
    score = forms.fields.ChoiceField(
        choices = (
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
        ),
        widget = forms.widgets.RadioSelect
    )
    
    class Meta:
        model = Review
        fields = (
            "score",
            "content",
        )

class ReservationForm(forms.ModelForm):
    reserved_time = forms.ChoiceField(label="予約時間")
    
    def __init__(self, request, seating_capacity, reservation_candidates, *args, **kwargs):
        self.request = request
        self.seating_capacity = seating_capacity
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields["reserved_time"].choices = reservation_candidates
    
    class Meta:
        model = Reservation                
        fields = (
            "reserved_date",
            "reserved_time",
            "number_of_people",
        )
        widgets = {
            "reserved_date": forms.NumberInput(attrs={
            "type": "date",
            "min": datetime.date.today() + relativedelta(days = 1) # 予約可能な一番早い日を翌日に設定
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('number_of_people') > self.seating_capacity:
            raise ValidationError('予約人数が多過ぎます。')

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label = "メールアドレス")

    class Meta:
        model = User
        fields = (
            "name",
            "kana_name",
            "email",
            "postal_code",
            "address",
            "tel_number",
            "birthday",
            "occupation",
        )
        this_year = datetime.date.today().year
        widgets = {
            "birthday": forms.SelectDateWidget(
                years=range(this_year - 120, this_year),
            ),
        }

class RestaurantForm(forms.ModelForm):
    holiday = forms.MultipleChoiceField(
        label="定休日",
        widget=forms.CheckboxSelectMultiple,
        choices = [(day.pk, day.holiday) for day in RegularHoliday.objects.all()]
    )
    
    category_name = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices = [(category.pk, category.category_name) for category in Category.objects.all()]
    )
     
    class Meta:
        model = Restaurant
        fields = (
            "restaurant_name",
            "image",
            "description",
            "lowest_price",
            "highest_price",
            "postal_code",
            "address",
            "opening_time",
            "closing_time",
            "holiday",
            "seating_capacity",
            "category_name",
        )
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('category_name') == None:
            cleaned_data.get('category_name') == []
        elif len(cleaned_data.get('category_name')) > 3:
            raise ValidationError('カテゴリは3つまで選択可能です')

