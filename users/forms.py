from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import forms
from .models import Employees


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput())
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput())
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(), required=False)
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(), required=False)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput())

    class Meta:
        model = Employees
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())
