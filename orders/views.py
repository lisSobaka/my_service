from typing import Any, Dict, List, Optional, Type
from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.forms import Form
from clients.forms import *
from .models import *
from .forms import *




# class OrdersView(PermissionRequiredMixin, ListView):
class OrdersView(ListView):
    # permission_required = ('clients.view_order')
    # login_url = reverse_lazy('login')
    model = Order
    template_name = 'orders.html'
    context_object_name = 'orders'
    paginate_by = 15
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_form'] = Form
        return context


class OrderDetail(PermissionRequiredMixin, DetailView):
    permission_required = ('clients.view_order')
    login_url = reverse_lazy('login')
    model = Order
    template_name = 'order.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_success_url(self):
        success_url = reverse_lazy('order', kwargs={'order_id': self.kwargs['order_id']})
        return success_url

    def get_context_data(self, **kwargs):
        context = self.object.get_order_data()
        context['order_history_form'] = OrderHistoryForm()
        return context


class DeleteOrder(DeleteView):
    model = Order
    pk_url_kwarg = 'order_id'
    template_name = 'delete_confirmation.html'
    success_url = reverse_lazy('orders')

    def get_context_data(self, **kwargs):
        context = self.object.get_order_data_cached()
        cancel_url = reverse_lazy('order', kwargs={'order_id': self.object.pk})
        context['cancel_button'] = cancel_url
        context['main_page'] = 'order.html'
        return context


class EditOrder(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'edit_order.html'
    pk_url_kwarg = 'order_id'
    
    def get_context_data(self, **kwargs):
        context = self.object.get_order_data_cached()
        if 'form' not in kwargs:
            context['form'] = OrderForm(instance=self.object)
        else:
            context['form'] = kwargs['form']
        return context
    

class CreateOrder(PermissionRequiredMixin, TemplateView):
    template_name = 'order_new.html'
    permission_required = ('clients.add_client', 'clients.add_order')
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_form'] = ClientForm()
        context['order_form'] = OrderForm(initial={'repairer': self.request.user.id})
        context['order_form'] = OrderForm(initial={'date_completion': datetime.now})
        print(self.request.user.last_login)
        return context
    
    def post(self, request):
        order_form = OrderForm(request.POST)
        client_form = ClientForm(request.POST)
        if client_form.is_valid() and order_form.is_valid():
            client = client_form.save()
            order = order_form.save(commit=False)
            order.client_id = client.pk
            order.save()
            OrderHistory.objects.create(
                    message = 'Заказ создан!',
                    order_id = order.pk,
                    repairer = order.repairer
                )
            # if order.prepayment:
            #     payment = Finance()
            #     payment.date = datetime.now()
            #     payment.income = order.prepayment
            #     payment.payment_reason = 'PREPAYMENT'
            #     payment.order_id = order.id
            #     payment.repairer_id = order.repairer_id
            #     payment.save()            
                
            #     OrderHistory.objects.create(
            #             message = 'Добавлена предоплата: ' + str(payment.income) + '  руб.',
            #             order_id = order.pk,
            #             repairer_id = self.request.user.pk
            #     )
                

            return HttpResponseRedirect(order.get_absolute_url())

        context = {
            'order_form': OrderForm(request.POST)
        }
        return render(request, "order_new.html", context)