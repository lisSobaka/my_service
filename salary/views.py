from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from users.models import Employees
from orders.models import Payments
from django.urls import reverse, reverse_lazy
from .models import Salary
from .forms import SalaryForm
from django.db.models import Sum, Q
from django.db import connection, reset_queries



def get_salary_data(employee_id):
    # Определяем список выполненных и неоплаченных работ, считаем и возвращаем их сумму
    unpaid_services = Salary.objects.filter(Q(employee_id=employee_id) & \
                                            Q(paid_for_employee=0))
    salary = unpaid_services.aggregate(Sum('amount'))['amount__sum']
    if not salary:
        salary = 0

    salary_data = {
        'unpaid_services': unpaid_services,
        'salary': salary
    }
    return salary_data
   

class MainSalary(ListView):
    model = Employees
    template_name = 'main_salary.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}
        context['employees'] = {}
        employees = Employees.objects.all()
        if employees:
            for employee in employees:
                context['employees'][employee] = get_salary_data(employee)['salary']
        return context


class EmployeeSalary(ListView):
    model = Salary
    template_name = 'employee_salary.html'
    context_object_name = 'salary'
    paginate_by = 15

    def get_queryset(self):
        queryset = Salary.objects.filter(employee=self.kwargs['employee_id']).order_by('-pk')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = Employees.objects.get(pk=self.kwargs['employee_id'])
        context['salary_amount'] = get_salary_data(context['employee'].pk)['salary']
        return context
    

class OperationsSalary(PermissionRequiredMixin, CreateView):
    permission_required = 'salary.add_salary'
    login_url = reverse_lazy('login')
    model = Salary
    template_name = 'operations_salary.html'
    form_class = SalaryForm

    def get_success_url(self):
        # ССылка на страницу ЗП мастера
        success_url = reverse_lazy('employee_salary', \
                                   kwargs={'employee_id': self.kwargs['employee_id']})
        return success_url
    
    def get_context_data(self, **kwargs):
        operation_type = self.request.GET.get('type')
        employee = Employees.objects.get(pk=self.kwargs['employee_id'])
        employee_salary_amount = get_salary_data(employee)['salary']

        context = super().get_context_data(**kwargs)
        context['salary'] = Salary.objects.select_related('employee')\
                            .filter(employee_id=self.kwargs['employee_id']).order_by('-pk')
        context['employee'] = employee

        if operation_type == 'payout':
            # Если операция - выплата ЗП: отправляем в форму его ЗП
            context['form'].initial={'amount': employee_salary_amount}
            context['form'].fields['amount'].widget.attrs['readonly'] = True
        context['salary_amount'] = employee_salary_amount
        return context

    def form_valid(self, form):
        operation_type = self.request.GET.get('type')
        if operation_type == 'payout':
            employee = Employees.objects.get(pk=self.kwargs['employee_id'])
            salary_data = get_salary_data(employee.pk)

            if salary_data['salary'] != 0:
                unpaid_services = salary_data['unpaid_services']

                # Если у матера не нулевая ЗП создаём запись о платеже в таблице Payments
                payment = Payments.objects.create(
                    expense = -salary_data['salary'],
                    comment = form.cleaned_data.get('comment'),
                    employee_id = self.request.user.pk,
                    payment_reason = 'SALARY_PAYOUT'
                )

                # Создаём запись в таблице Salary
                operation = form.save(commit=False)
                operation.amount = -salary_data['salary']
                operation.paid_for_employee = True
                operation.employee_id = employee.pk
                operation.payment_id = payment.pk
                operation.reason = 'PAYOUT'
                operation.save()

                # Для каждой неоплаченной услуги меняем статус "оплачено мастеру",
                # записываем услуге id операции оплаты, чтобы можно было вернуть статус 
                # услугам при удалении операции оплаты
                for service in unpaid_services:
                    service.paid_for_employee=True
                    service.paid_by_operation = operation.pk
                Salary.objects.bulk_update(unpaid_services, ['paid_for_employee', 'paid_by_operation'])
            return redirect(self.get_success_url())
        
        # Если операция - премия, штраф или промежуточная выплата - создаём запись только
        # в таблице Salary, т.к. в общей Payments она в любом случае отразится 
        # в момент выплаты ЗП
        elif operation_type == 'bonus' or \
             operation_type == 'penalty' or \
             operation_type == 'interim_payment':
            
            operation = form.save(commit=False)
            operation.employee_id = self.kwargs['employee_id']
            operation.reason = operation_type.upper()
            if operation_type == 'penalty' or \
               operation_type == 'interim_payment':
               operation.amount = -operation.amount

            operation.save()

        return super().form_valid(form)
    

class DeleteOperationsSalary(PermissionRequiredMixin, DeleteView):
    permission_required = 'salary.delete_salary'
    login_url = reverse_lazy('login')
    model = Salary
    pk_url_kwarg = 'operation_id'
    template_name = 'delete_confirmation.html'

    def get_success_url(self):
        success_url = reverse_lazy('employee_salary', \
                                   kwargs={'employee_id': self.kwargs['employee_id']})
        return success_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salary'] = Salary.objects.filter(employee_id=self.kwargs['employee_id'])\
                            .select_related('employee').order_by('-pk')
        context['employee'] = Employees.objects.get(pk=self.kwargs['employee_id'])
        context['main_page'] = 'employee_salary.html'
        context['cancel_button'] = reverse_lazy('employee_salary', \
                                                kwargs={'employee_id': self.kwargs['employee_id']})
        context['salary_amount'] = get_salary_data(self.kwargs['employee_id'])['salary']
        return context
    
    def form_valid(self, form):
        if self.object.reason == 'PAYOUT':
            salary_operaiton = self.object
            make_works_unpaid(salary_operaiton)
            Payments.objects.get(pk=salary_operaiton.payment_id).delete()
        return super().form_valid(form)
    

# Находим услуги, выплаченные мастеру переданной операцией, делаем их не выплаченными
def make_works_unpaid(salary_operation):
    paid_works = Salary.objects.filter(Q(paid_for_employee=True) & 
                                       Q(paid_by_operation=salary_operation.pk))
    for work in paid_works: 
        work.paid_for_employee = False 
    Salary.objects.bulk_update(paid_works, ['paid_for_employee'])
        