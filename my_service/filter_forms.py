from django import forms
from users.models import Employees


class DateInput(forms.DateInput):
    input_type = 'date'


class FilterDateForm(forms.Form):
    FILTER_SELECTIONS = (
        ('', 'Выбрать дату'),
        ('today', 'Сегодня'),
        ('yesterday', 'Вчера'),
        ('week', 'С начала недели'),
        ('month', 'С начала месяца'),
        ('last_month', 'Прошлый месяц'),
        ('year', 'С начала года'),
        ('interval', 'Выбрать промежуток')
    )

    date = forms.ChoiceField(label='Дата:', 
                             required=False,
                             choices=FILTER_SELECTIONS,
                             widget=forms.Select(attrs={'id': 'date_selector',
                                                        'onchange': 'showHideCalendar(this.value)',}))
    start = forms.CharField(label='Начало интервала:', 
                            widget=DateInput(attrs={'disabled': True,
                                                    'hidden': True,
                                                    'id': 'interval_start',}))
    end = forms.CharField(label='Конец интервала:', 
                          widget=DateInput(attrs={'disabled': True,
                                                  'hidden': True,
                                                  'id': 'interval_end',}))
    

class FilterEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = ['id']

    employee = forms.ModelChoiceField(label='Сотрудник', 
                                      required=False,
                                      empty_label='Выбрать сотрудника',
                                      queryset=Employees.objects.all(),
                                      widget=forms.Select())