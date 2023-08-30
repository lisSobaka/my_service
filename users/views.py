from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from .forms import RegisterUserForm, LoginUserForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('orders')

    def post(self, request, **kwargs):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.groups.add(Group.objects.get(name='Repairer'))

            # login(request, user)

            return render(request, 'register_success.html')
        
        context = {'form': form}
        return render (request, self.template_name, context)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'
    # success_url = reverse_lazy('orders')

    # def get_success_url(self):
    #     return self.success_url
    
