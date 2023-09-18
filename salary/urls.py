from django.urls import path
from .views import *


urlpatterns = [
    path('', MainSalary.as_view(), name='main_salary'),
    path('<int:employee_id>/', EmployeeSalary.as_view(), name='employee_salary'),
    path('<int:employee_id>/operations', OperationsSalary.as_view(), name='operations_salary'),
    path('<int:employee_id>/delete_operation_salary/<int:operation_id>', DeleteOperationsSalary.as_view(), name='delete_operation_salary'),
]