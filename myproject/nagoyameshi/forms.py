from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User, Review, Reservation, Restaurant, RegularHoliday, Category
from dateutil.relativedelta import relativedelta
import datetime

postal_code_regex = RegexValidator(regex=r'^[0-9]{7}$', message = ("郵便番号は半角数字7文字で入力してください"))

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder':'名古屋 太郎',})
        self.fields['kana_name'].widget.attrs.update({'placeholder':'ナゴヤ タロウ',})
        self.fields['nick_name'].widget.attrs.update({'placeholder':'タロちゃん',})
        self.fields['email'].widget.attrs.update({'placeholder': 'tarou@nagoyameshi.com',})
        self.fields['postal_code'].widget.attrs.update({'placeholder': '0123456',})
        self.fields['address'].widget.attrs.update({'placeholder': '愛知県栄区X-X-X',})
        self.fields['tel_number'].widget.attrs.update({'placeholder': '09012345678',})
        self.fields['password1'].widget.render_value = True
        self.fields['password2'].widget.render_value = True
            
    email = forms.EmailField(label = "メールアドレス")

    class Meta:
        model = User
        fields = (
            "name",
            "kana_name",
            "nick_name",
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

class ReservationInputForm(forms.ModelForm):
    reserved_time = forms.ChoiceField(label="予約時間")
    
    def __init__(self, request, seating_capacity, reservation_candidates, *args, **kwargs):
        self.request = request
        self.seating_capacity = seating_capacity
        super(ReservationInputForm, self).__init__(*args, **kwargs)
        self.fields["reserved_time"].choices = reservation_candidates
        self.fields['number_of_people'].widget.attrs['min'] = 1
        self.fields['number_of_people'].widget.attrs['max'] = seating_capacity
            
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

class ReservationConfirmForm(forms.ModelForm):
    class Meta:
        model = Reservation                
        fields = (
            "reserved_date",
            "reserved_time",
            "number_of_people",
        )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label = "メールアドレス")

    class Meta:
        model = User
        fields = (
            "name",
            "kana_name",
            "nick_name",
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

class RestaurantCreateForm(forms.ModelForm):
    holiday = forms.MultipleChoiceField(
        label="定休日",
        widget=forms.CheckboxSelectMultiple,
        choices = [(day.holiday_index, day.holiday) for day in RegularHoliday.objects.all()],
        required = True,
    )
    
    category_name = forms.MultipleChoiceField(
        label="カテゴリ（3つまで選択可）",
        widget=forms.CheckboxSelectMultiple,
        choices = [(category.pk, category.category_name) for category in Category.objects.all()],
        required = True,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['postal_code'].widget.attrs.update({'placeholder': '0123456',})
        self.fields['opening_time'].widget.attrs.update({'placeholder': '11:00',})
        self.fields['closing_time'].widget.attrs.update({'placeholder': '23:00',})
        self.fields['seating_capacity'].widget.attrs['min'] = 1
    
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
        
    def clean_holiday(self):
        holiday = self.cleaned_data["holiday"]
        if "8" in holiday or "9" in holiday:
            if len(holiday) > 1:
                raise ValidationError("「不定休」または「なし」と他の項目を同時に選択しないでください")
        elif "1" in holiday and "2" in holiday and "3" in holiday and "4" in holiday and "5" in holiday and "6" in holiday and "7" in holiday:
            raise ValidationError("定休日を正しく設定してください")
        return holiday
    
    def clean_category_name(self):
        category_name = self.cleaned_data["category_name"]
        if category_name == None:
            pass
        elif len(category_name) > 3:
            raise forms.ValidationError('カテゴリは3つまで選択可能です')
        return category_name

    def clean(self):
        cleaned_data = super().clean()
        lowest_price = cleaned_data.get("lowest_price")
        highest_price = cleaned_data.get("highest_price")
        if lowest_price >= highest_price:
            raise forms.ValidationError("最高価格は最低価格以上に設定してください")
        return cleaned_data

class RestaurantEditForm(forms.ModelForm):
    holiday = forms.MultipleChoiceField(
        label="定休日",
        widget=forms.CheckboxSelectMultiple,
        choices = [(day.pk, day.holiday) for day in RegularHoliday.objects.all()],
        required = True,
    )
    
    category_name = forms.MultipleChoiceField(
        label="カテゴリ（3つまで選択可）",
        widget=forms.CheckboxSelectMultiple,
        choices = [(category.pk, category.category_name) for category in Category.objects.all()],
        required = True,
    )
    
    def __init__(self, holidays, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['postal_code'].widget.attrs.update({'placeholder': '0123456',})
        self.fields['opening_time'].widget.attrs.update({'placeholder': '11:00',})
        self.fields['closing_time'].widget.attrs.update({'placeholder': '23:00',})
        self.initial['holiday'] = holidays #forms.pyで設定したholidayの初期値を代入
        self.initial['category_name'] = categories
        self.fields['seating_capacity'].widget.attrs['min'] = 1
    
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
        
    def clean_holiday(self):
        holiday = self.cleaned_data["holiday"]
        if "9" in holiday:
            if len(holiday) > 1:
                raise ValidationError("「なし」と他の項目を同時に選択しないでください")
        elif "1" in holiday and "2" in holiday and "3" in holiday and "4" in holiday and "5" in holiday and "6" in holiday and "7" in holiday:
            raise ValidationError("定休日を正しく設定してください")
        return holiday
    
    def clean_category_name(self):
        category_name = self.cleaned_data["category_name"]
        if category_name == None:
            pass
        elif len(category_name) > 3:
            raise forms.ValidationError('カテゴリは3つまで選択可能です')
        return category_name
    
    def clean(self):
        cleaned_data = super().clean()
        lowest_price = cleaned_data.get("lowest_price")
        highest_price = cleaned_data.get("highest_price")
        if lowest_price >= highest_price:
            raise forms.ValidationError("最高価格は最低価格以上に設定してください")
        return cleaned_data

class UserSearch(forms.Form):
    status_choice = [
        (1, "会員"),
        (2, "退会"),
        (3, "未選択"),
    ]
    
    name = forms.CharField(required=False, label="名前で検索")
    email = forms.CharField(required=False, label="メールアドレスで検索")
    tel = forms.CharField(required=False, label="電話番号で検索")
    address = forms.CharField(required=False, label="住所で検索（会員のみ）")
    status = forms.ChoiceField(required=False, widget=forms.RadioSelect, choices=status_choice)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': '漢字・カナ・ニックネーム',})
        self.fields['address'].widget.attrs.update({'placeholder': '郵便番号（ハイフンなし）・住所',})

class ReservedUserSearch(forms.Form):
    query = forms.CharField(required=False, label="予約者情報で検索")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['query'].widget.attrs.update({'placeholder': '氏名（漢字・カナ）・電話番号',})

class RestaurantSearch(forms.Form):
    query = forms.CharField(required=False, label="キーワード検索")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['query'].widget.attrs.update({'placeholder': '店舗名・郵便番号（ハイフンなし）・住所',})
