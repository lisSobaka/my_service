from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView
from users.models import Employees
from orders.models import Payments
from django.urls import reverse, reverse_lazy
from .models import Salary
from .forms import SalaryForm
from django.db.models import Sum


def get_salary_data(employee_id):
    unpaid_services = Salary.objects.filter(employee_id=employee_id) & Salary.objects.filter(paid_for_employee=0)
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
    ordering = ['-pk']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(employee_id = self.kwargs['employee_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = Employees.objects.get(pk=self.kwargs['employee_id'])
        context['salary_amount'] = get_salary_data(context['employee'].pk)['salary']
        return context
    

class OperationsSalary(CreateView):
    model = Salary
    template_name = 'operations_salary.html'
    form_class = SalaryForm

    def get_success_url(self):
        success_url = reverse_lazy('employee_salary', kwargs={'employee_id': self.kwargs['employee_id']})
        return success_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salary'] = Salary.objects.select_related('employee').filter(employee_id=self.kwargs['employee_id']).order_by('-pk')
        if context['salary']:
            context['employee'] = context['salary'][0].employee
        else:
            context['employee'] = Employees.objects.get(pk=self.kwargs['employee_id'])
        if self.request.GET.get('type') == 'payout':
            employee = Employees.objects.get(pk=self.kwargs['employee_id'])
            context['form'].initial={'amount': get_salary_data(employee.pk)['salary']}
            context['form'].fields['amount'].widget.attrs['readonly'] = True
        context['salary_amount'] = get_salary_data(context['employee'].pk)['salary']
        return context

    def form_valid(self, form):
        if self.request.GET.get('type') == 'payout':
            employee = Employees.objects.get(pk=self.kwargs['employee_id'])
            salary_data = get_salary_data(employee.pk)
            if salary_data['salary'] != 0:
                unpaid_services = salary_data['unpaid_services']
                operation = form.save(commit=False)

                payment = Payments.objects.create(
                    expense = salary_data['salary'],
                    comment = form.cleaned_data.get('comment'),
                    employee_id = self.request.user.pk,
                    payment_reason = 'SALARY_PAYOUT'
                )

                operation.amount = -salary_data['salary']
                operation.paid_for_employee = True
                operation.employee_id = employee.pk
                operation.payment_id = payment.pk
                operation.reason = 'PAYOUT'
                operation.save()

                for service in unpaid_services:
                    service.paid_for_employee=True
                    service.paid_by_operation = operation.pk
                    service.save()
            return redirect(self.get_success_url())
            
        elif self.request.GET.get('type') == 'bonus' or self.request.GET.get('type') == 'penalty' or self.request.GET.get('type') == 'interim_payment':
            operation = form.save(commit=False)
            operation.employee_id = self.kwargs['employee_id']
            operation.reason = self.request.GET.get('type').upper()
            if self.request.GET.get('type') == 'penalty' or self.request.GET.get('type') == 'interim_payment':
                operation.amount = -operation.amount
            operation.save()

        return super().form_valid(form)
    

class DeleteOperationsSalary(DeleteView):
    model = Salary
    pk_url_kwarg = 'operation_id'
    template_name = 'delete_confirmation.html'

    def get_success_url(self):
        success_url = reverse_lazy('employee_salary', kwargs={'employee_id': self.kwargs['employee_id']})
        return success_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salary'] = Salary.objects.filter(employee_id=self.kwargs['employee_id']).select_related('employee').order_by('-pk')
        context['employee'] = Employees.objects.get(pk=self.kwargs['employee_id'])
        context['main_page'] = 'employee_salary.html'
        context['cancel_button'] = reverse_lazy('employee_salary', kwargs={'employee_id': self.kwargs['employee_id']})
        context['salary_amount'] = get_salary_data(self.kwargs['employee_id'])['salary']
        return context
    
    def form_valid(self, form):
        if self.object.reason == 'PAYOUT':
            paid_sevices = Salary.objects.filter(paid_for_employee=True) & Salary.objects.filter(paid_by_operation=self.object.pk)
            for service in paid_sevices:
                service.paid_for_employee = False
                service.save()
        return super().form_valid(form)