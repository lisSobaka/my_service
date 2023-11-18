from typing import Any
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from .forms import RegisterUserForm, LoginUserForm
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from .models import Employees
from django.contrib.auth import login 
from salary.models import Salary


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = 'register_success.html'

    def post(self, request, **kwargs):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Group.objects.get_or_create(name='Repairer')

            user.groups.add(Group.objects.get(name='Repairer'))

            # login(request, user)
            return render(request, self.success_url)
        
        context = {'form': form}
        return render (request, self.template_name, context)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        form = self.request.POST
        if form['demo']:
            if form['demo'] == 'demo_login_admin':
                user = Employees.objects.get(username='admin')
            elif form['demo'] == 'demo_login_employee':
                user = Employees.objects.get(username='employee')
            login(request, user)
            return redirect('orders')
        
        return super().post(request, *args, **kwargs)