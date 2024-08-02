from django.contrib.auth.forms import UserCreationForm
from .models import User, Restaurant
#, Category, RegularHoliday
from django.core.exceptions import ValidationError
from django import forms

class SignUpForm(UserCreationForm):
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
        )

class PasswordresetForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
        )
        
#class RestaurantAdminForm(forms.ModelForm):
#    def clean(self):
#        cleaned_data = super().clean()
#        if cleaned_data.get('category_name') == None:
#            cleaned_data.get('category_name') == []
#        elif len(cleaned_data.get('category_name')) > 3:
#            raise ValidationError('カテゴリは3つまで選択可能です')

#    holiday = forms.MultipleChoiceField(
#        choices = RegularHoliday.objects.values_list('holiday', 'holiday').distinct(),
#        label = '定休日',
#        widget = forms.CheckboxSelectMultiple,
#        required = False,
#        )
    
#    category_name = forms.MultipleChoiceField(
#        choices = Category.objects.values_list('category_name', 'category_name').distinct(),
#        label = 'カテゴリ（3つまで選択可）',
#        widget = forms.CheckboxSelectMultiple,
#        required = False,
#        )
