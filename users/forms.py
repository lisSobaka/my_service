from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Employees


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(
        attrs={'class': 'text-field__input', 'placeholder': 'username'}))
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(
        attrs={'class': 'text-field__input', 'placeholder': 'email'}))
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(
        attrs={'class': 'text-field__input', 'placeholder': 'first_name'}), required=False)
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(
        attrs={'class': 'text-field__input', 'placeholder': 'last_name'}), required=False)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'class': 'text-field__input', 'placeholder': 'password1'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(
        attrs={'class': 'text-field__input', 'placeholder': 'password2'}))

    class Meta:
        model = Employees
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(
        attrs={'autofocus': True, 'class': 'text-field__input', 'placeholder': 'username'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'class': 'text-field__input', 'placeholder': 'password'}))
