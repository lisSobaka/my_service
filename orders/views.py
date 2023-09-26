from typing import Any, Dict, List, Optional, Type
from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, TemplateView, CreateView, FormView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.forms import Form
from clients.forms import *
from .models import *
from .forms import *
from salary.models import Salary
from salary.views import make_works_unpaid
from django.db.models import Sum


class OrdersView(PermissionRequiredMixin, ListView):
    permission_required = 'orders.view_order'
    login_url = reverse_lazy('login')
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
    permission_required = 'orders.view_order'
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


class DeleteOrder(PermissionRequiredMixin, DeleteView):
    permission_required = 'orders.delete_order'
    login_url = reverse_lazy('login')
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


class EditOrder(PermissionRequiredMixin, UpdateView):
    permission_required = 'orders.change_order'
    login_url = reverse_lazy('login')
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
    permission_required = ('clients.add_client', 'orders.add_order')
    login_url = reverse_lazy('login')
    template_name = 'order_new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_form'] = ClientForm()
        context['order_form'] = OrderForm(initial={'employee': self.request.user.id, 'date_completion': datetime.now})
        print(self.request.user.id)
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
                    employee = order.employee
                )
            if order.prepayment:
                payment = Payments()
                payment.date = datetime.now()
                payment.income = order.prepayment
                payment.payment_reason = 'PREPAYMENT'
                payment.order_id = order.id
                payment.employee_id = order.employee_id
                payment.save()            
                
                OrderHistory.objects.create(
                        message = 'Добавлена предоплата: ' + str(payment.income) + '  руб.',
                        order_id = order.pk,
                        employee_id = self.request.user.pk
                )
            return HttpResponseRedirect(order.get_absolute_url())
        context = {
            'order_form': OrderForm(request.POST)
        }
        return render(request, "order_new.html", context)
    

class AddPayment(PermissionRequiredMixin, CreateView):
    permission_required = 'orders.create_payment'
    login_url = reverse_lazy('login')
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
        payment.employee_id = self.request.user.id
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
                employee_id = self.request.user.pk
            )
        payment.save()

        return HttpResponseRedirect(success_url)


class PaymentsView(PermissionRequiredMixin, ListView):
    permission_required = 'orders.view_payments'
    login_url = reverse_lazy('login')
    ordering = ['-pk']
    model = Payments
    template_name = 'payments.html'
    context_object_name = 'payments'
    paginate_by = 15

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['all_income'] = context['payments'].aggregate(Sum('income'))['income__sum']
        context['all_expense'] = context['payments'].aggregate(Sum('expense'))['expense__sum']
        context['all_profit'] = context['all_income'] - context['all_expense']

        # Кэшируем контекст для страницы удаления платежей. Вьюху удаляю, т.к. с ней не кэширует
        cached_context = context
        del(cached_context['view'])
        cache.set_many({'cached_context': cached_context})

        return context
    
    # def get_context_data_cached():
    #     if not 

    
class DeletePayment(PermissionRequiredMixin, DeleteView):
    permission_required = 'orders.delete_payments'
    login_url = reverse_lazy('login')
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
            # Забираем контекст из кэша (он формируется в классе PaymentsView)
            context = cache.get('cached_context')
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
            OrderHistory.objects.create(
                message = history_message,
                order_id = payment.order_id,
                employee_id = self.request.user.pk
            )

        # Если платёж выдавал ЗП - находим соответствующую выплату, делаем выплаченные ей услуги неоплаченными мастеру и удаляем её
        if payment.payment_reason == 'SALARY_PAYOUT':
            salary_operation = Salary.objects.get(payment_id=payment.pk)
            make_works_unpaid(salary_operation)
            salary_operation.delete()
        return super().form_valid(form)


def add_history_message(request, order_id):
    if request.method == 'POST':
        message_form = OrderHistoryForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.order_id = order_id
            message.employee_id = request.user.pk
            message.save()
    return redirect('order', order_id)


class EditWork(PermissionRequiredMixin, UpdateView):
    permission_required = 'orders.change_works'
    login_url = reverse_lazy('login')
    model = Works
    form_class = WorkForm
    pk_url_kwarg = 'work_id'
    template_name = 'edit_work.html'

    def get_success_url(self) -> str:
        success_url = reverse_lazy('order', kwargs={'order_id': self.kwargs['order_id']})
        return success_url

    def get_context_data(self, **kwargs):
        order = Order.objects.get(pk=self.kwargs['order_id'])
        context = order.get_order_data_cached()
        if 'form' not in kwargs:
            context['form'] = WorkForm(instance=Works.objects.get(pk=self.kwargs['work_id']))
        else:
            context['form'] = kwargs['form']
        return context
    
    
class AddWork(PermissionRequiredMixin, CreateView):
    permission_required = 'orders.add_works'
    login_url = reverse_lazy('login')
    model = Works
    form_class = WorkForm
    template_name = 'add_work.html'

    def get_context_data(self, **kwargs):
        order = Order.objects.get(pk=self.kwargs['order_id'])
        context = order.get_order_data_cached()
        if 'form' not in kwargs:
            context['form'] = WorkForm(initial={'employee': self.request.user.pk})
        else:
            context['form'] = kwargs['form']
        return context
    
    def form_valid(self, form):
        work = form.save(commit=False)
        work.order_id = self.kwargs['order_id']
        work.save()
        OrderHistory.objects.create(
            message = 'Добавлена услуга: ' + work.work,
            order_id = work.order_id,
            employee_id = self.request.user.pk
        )

        return redirect('order', self.kwargs['order_id'])
    

class DeleteWork(PermissionRequiredMixin, DeleteView):
    permission_required = 'orders.delete_works'
    login_url = reverse_lazy('login')
    model = Works
    template_name = 'delete_confirmation.html'
    pk_url_kwarg = 'work_id'
    success_url = reverse_lazy('orders')

    def get_context_data(self, **kwargs):
        order = Order.objects.get(pk=self.kwargs['order_id'])
        context = order.get_order_data_cached()
        context['cancel_button'] = order.get_absolute_url()
        context['main_page'] = 'order.html'
        context['form'] = Form()
        return context
    
    def form_valid(self, form):
        OrderHistory.objects.create(
            message = 'Удалена услуга: ' + self.object.work,
            order_id = self.object.order_id,
            employee_id = self.request.user.pk
        )
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse_lazy('order', kwargs={'order_id': self.kwargs['order_id']})


class CloseOrder(PermissionRequiredMixin, FormView):
    permission_required = 'orders.change_order'
    login_url = reverse_lazy('login')
    model = Payments
    template_name = 'add_payment.html'
    form_class = PaymentsIncomeForm
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        order = Order.objects.get(pk=self.kwargs['order_id'])
        context = order.get_order_data_cached()
        context['form'] = super().get_form()
        context['form'].fields['income'].widget.attrs['readonly'] = True
        context['form'].initial={'income': order.get_finance_data()['client_debt']}
        return context
    
    def form_valid(self, form: Any) -> HttpResponse:
        order = Order.objects.get(pk=self.kwargs['order_id'])
        works = Works.objects.filter(order_id = order.pk)
        order.in_work = False
        order.save()

        payment = form.save(commit=False)
        payment.income = order.get_finance_data()['client_debt']
        payment.order_id = order.pk
        payment.employee_id = self.request.user.pk
        payment.payment_reason = 'ORDER_PAYMENT'
        payment.save()

        OrderHistory.objects.create(
            message = 'Заказ закрыт! Добавлен платёж: ' + str(payment.income) + ' руб.',
            order_id = payment.order_id,
            employee_id = self.request.user.pk
        )

        # Проверяем все работы в заказе, если есть не оплаченные клиентом, добавляем их в ЗП мастеру,
        # меняем статус на 'оплачен клиентом', присваиваем работе номер платежа
        for work in works:
            if not work.paid_by_client:
                salary = Salary.objects.get_or_create(
                    amount = (work.price - work.cost - work.discount) * work.quantity * (work.employee.percent/100),
                    order_id = order.pk,
                    employee_id = work.employee.pk,
                    work_id = work.pk
                )
                work.paid_by_client = True
                work.payment_id = payment.pk
                print('!!!!!!!!!!!!!!!!!!', work.payment)
                work.save()
        return redirect('order', order.pk)