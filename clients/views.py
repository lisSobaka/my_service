from django.shortcuts import render
from .models import *
from orders.models import *
from .forms import *
from django.views.generic import UpdateView, ListView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin


class ClientsView(PermissionRequiredMixin, ListView):
    permission_required = 'clients.view_client'
    login_url = reverse_lazy('login')
    model = Client
    template_name = 'clients.html'
    context_object_name = 'clients'
    paginate_by = 15


class EditClient(PermissionRequiredMixin, UpdateView):
    permission_required = 'clients.change_client'
    login_url = reverse_lazy('login')
    model = Client
    form_class = ClientForm
    template_name = 'edit_client.html'
    pk_url_kwarg = 'client_id'

    def get_success_url(self):
        if 'order_id' in self.request.GET:
            success_url = reverse_lazy('order', kwargs={'order_id': self.request.GET.get('order_id')})
        else:
            success_url = reverse_lazy('clients')
        return success_url

    def get_context_data(self, **kwargs):
        context = {}
        if 'order_id' in self.request.GET:
            order = Order.objects.get(pk=self.request.GET.get('order_id'))
            context = order.get_order_data_cached()
            context['template_name'] = 'order.html'

        else:
            context['clients'] = Client.objects.all()
            context['template_name'] = 'clients.html'

        if 'form' not in kwargs:
            context['form'] = ClientForm(instance=self.object)
        else:
            context['form'] = kwargs['form']
        return context