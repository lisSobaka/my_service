from django import forms
from users.models import Employees
from datetime import date, datetime, timedelta


def get_interval(self):
    # Проверяю, какой временной интервал передан в GET, высчитываю и отправляю 
    # start и end для дальнейшего формирования queryset
    needed_date = self.request.GET.get('date')
    today = date.today()
    end = today + timedelta(days=1)
    
    if needed_date == 'today':
        start = today

    elif needed_date == 'yesterday':
        start = today - timedelta(days=1)
        end = today

    elif needed_date == 'week':
        start = today - timedelta(days=date.weekday(today))

    elif needed_date == 'month':
        start = today - timedelta(days=date.today().day - 1)

    elif needed_date == 'last_month':
        end = date(date.today().year, date.today().month, 1) - timedelta(days=1)
        start = end - timedelta(days=end.day - 1)

    elif needed_date == 'year':
        start = date(date.today().year, 1, 1)

    elif needed_date == 'interval':
        start = self.request.GET.get('start')
        # По какой-то причине в конце не добирает один день, тут я привожу к
        # формату даты и добавляю этот день
        end = datetime.strptime(self.request.GET.get('end'), "%Y-%m-%d") + timedelta(days=1)

    interval = {
        'start': start,
        'end': end,
    }
    return interval


def get_filtered_queryset(self):
    # Проверяю, какие параметры переданы в GET, получаю start и end через функцию get_interval 
    # и формирую queryset с учётом параметров фильтра
    if self.request.GET.get('date') and self.request.GET.get('employee'):
        interval = get_interval(self)
        queryset = self.model.objects.filter(date_creation__range=(interval['start'], interval['end'])) & \
                   self.model.objects.filter(employee_id=self.request.GET.get('employee'))
        
    elif self.request.GET.get('date'):
        interval = get_interval(self)
        queryset = self.model.objects.filter(date_creation__range=(interval['start'], interval['end']))

    elif self.request.GET.get('employee'):
        queryset = self.model.objects.filter(employee_id=self.request.GET.get('employee'))

    else:
        queryset = self.model.objects.all()

    return queryset


def get_initialized_forms(self, context):
    # Инициализирую и добавляю в контекст Select'ы для фильтра
    context['filter_date_form'] = FilterDateForm(initial={'date': self.request.GET.get('date'),
                                                            'start': self.request.GET.get('start'),
                                                            'end': self.request.GET.get('end')})
    context['filter_employee_form'] = FilterEmployeeForm(initial={
                                                            'employee': self.request.GET.get('employee')})
    
    return context


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