from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Review,Reservation

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(AuthenticationForm):
    pass

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class ReservationForm(forms.ModelForm):
    class Meta:
        model=Reservation
        fields=['date','time','number_of_people']
        labels = {
            'date': '予約日',
            'time': '予約時間',
            'number_of_people': '人数',
        }
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': '2025-12-31'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'placeholder': '18:00'
            }),
            'number_of_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': '例: 2'
            }),
        }

class SearchForm(forms.Form):
    query=forms.CharField(label='検索',max_length=100,required=False)
