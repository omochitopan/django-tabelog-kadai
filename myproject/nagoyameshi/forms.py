from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms
from .models import User, Review, Reservation
from dateutil.relativedelta import relativedelta
import datetime

class SignUpForm(UserCreationForm):
    name = forms.CharField(label = "お名前（漢字）", widget=forms.TextInput(attrs={'placeholder': '名古屋 太郎'}))
    kana_name = forms.CharField(label = "フリガナ", widget=forms.TextInput(attrs={'placeholder': 'ナゴヤ タロウ'}))
    email = forms.EmailField(label = "メールアドレス", widget=forms.EmailInput(
        attrs={'placeholder': 'tarou@nagoyameshi.com'}
        ))
    postal_code = forms.IntegerField(label = "郵便番号", widget=forms.TextInput(attrs={'placeholder': '1234567'}))
    address = forms.CharField(label = "住所", widget=forms.TextInput(attrs={'placeholder': '愛知県栄区X-X-X'}))
    tel_number = forms.IntegerField(label = "電話番号", widget=forms.TextInput(attrs={'placeholder': '09012345678'}))

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
    class Meta:
        model = User
        fields = (
            "name",
            "kana_name",
            "postal_code",
            "address",
            "tel_number",
            "birthday",
            "occupation",
            "email",
        )
        this_year = datetime.date.today().year
        widgets = {
            "birthday": forms.SelectDateWidget(
                years=range(this_year - 120, this_year),
            ),
        }
