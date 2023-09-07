from django.db import models
from django.contrib.auth.models import AbstractUser


class Employees(AbstractUser):
    percent = models.IntegerField(verbose_name='Процент от заказа', default=50)
    earnings = models.IntegerField(default=0, verbose_name='Заработок с последней выплаты')

    def __str__(self) -> str:
        full_name = super().get_full_name()
        return full_name

    # def get_salary_data(self):
    #     unpaid_services = Salary.objects.filter(employee_id=self.pk) & Salary.objects.filter(paid_for_employee=0)
    #     salary = unpaid_services.aggregate(Sum('amount'))['amount__sum']
    #     if not salary:
    #         salary = 0
    #     salary_data = {
    #         'unpaid_services': unpaid_services,
    #         'salary': salary
    #     }
    #     return salary_data
