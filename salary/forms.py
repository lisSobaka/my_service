from django import forms
from .models import Salary


class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['amount', 'comment']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'amount'}),
            'comment': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'comment'})
        }