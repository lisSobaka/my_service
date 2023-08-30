from typing import Any, Dict, List, Optional, Type
from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, TemplateView, CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404
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
    

class AddPayment(CreateView):
    model = Payments
    template_name = 'add_payment.html'
    
    def get_form_class(self):
        if self.request.GET.get('type') == 'prepayment':
            self.form_class = PaymentsIncomeForm
        elif self.request.GET.get('type') == 'refund':
            self.form_class = PaymentsExpenseForm
        else:
            raise Http404
        return super().get_form_class()
    
    def get_context_data(self, **kwargs):
        order = Order.objects.get(pk=self.request.GET.get('order_id'))
        context = order.get_order_data_cached()
        context['form'] = self.get_form_class()
        return context
    
    def form_valid(self, form):
        success_url = reverse_lazy('payments')
        payment = form.save(commit=False)
        # payment.repairer_id = self.request.user.id
        payment.expense = -payment.expense
        payment.payment_reason = self.request.GET.get('type').upper()

        if self.request.GET.get('order_id'):
            order_id = self.request.GET.get('order_id')
            success_url = reverse_lazy('order', kwargs={'order_id': order_id})
            payment.order_id = order_id
            print(payment.payment_reason)

            if payment.payment_reason == 'PREPAYMENT':
                history_message = 'Добавлена предоплата: ' + str(payment.income) + '  руб.'
            elif payment.payment_reason == 'REFUND':
                history_message = 'Добавлен возврат предоплаты: ' + str(payment.expense) + '  руб.'

            OrderHistory.objects.create(
                message = history_message,
                order_id = payment.order_id,
                # repairer_id = self.request.user.pk
            )
        payment.save()

        return HttpResponseRedirect(success_url)


class PaymentsView(ListView):
    ordering = ['-pk']
    model = Payments
    template_name = 'payments.html'
    context_object_name = 'payments'

    
class DeletePayment(PermissionRequiredMixin, DeleteView):
    permission_required = 'clients.delete_finance'
    model = Payments
    template_name = 'delete_confirmation.html'
    pk_url_kwarg = 'payment_id'

    def get_success_url(self):
        if 'order_id' in self.request.GET:
            success_url = reverse_lazy('order', kwargs={'order_id': self.request.GET.get('order_id')})
        else:
            success_url = reverse_lazy('payments')
        return success_url

    def get_context_data(self, **kwargs):
        if 'order_id' in self.request.GET:
            order = Order.objects.get(pk=self.request.GET.get('order_id'))
            context = order.get_order_data_cached()
            context['cancel_button'] = order.get_absolute_url()
            context['main_page'] = 'order.html'
        else:
            context = {}
            context['finance'] = Payments.objects.all().order_by('-pk')
            context['form'] = Form()
            context['cancel_button'] = reverse_lazy('payments')
            context['main_page'] = 'payments.html'
        return context
    
    def form_valid(self, form):
        payment = self.object
        if payment.order_id:
            if payment.payment_reason == 'PREPAYMENT':
                history_message = 'Удалена предоплата: ' + str(payment.income) + ' руб.'
            elif payment.payment_reason == 'REFUND':
                history_message = 'Удален возврат предоплаты: ' + str(payment.expense) + ' руб.'

            elif payment.payment_reason == 'ORDER_PAYMENT':
                history_message = 'Удалена оплата заказа: ' + str(payment.income) + ' руб.'
                paid_works = Works.objects.filter(payment_id=payment.pk)
                for work in paid_works:
                    work.paid_by_client = False
                    work.save()

        # OrderHistory.objects.create(
        #     message = history_message,
        #     order_id = payment.order_id,
        #     repairer_id = self.request.user.pk
        # )
        return super().form_valid(form)



def add_history_message(request, order_id):
    if request.method == 'POST':
        message_form = OrderHistoryForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.order_id = order_id
            # message.repairer_id = request.user.pk
            message.save()
    return redirect('order', order_id)

