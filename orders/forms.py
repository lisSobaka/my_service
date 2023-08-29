from django import forms
from .models import *


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['whats_broken', 'device_appearance', 'device_type', 'imei', 'device_brand',
                  'device_model', 'device_kit', 'device_pass', 'price', 'prepayment',
                  'repairer', 'note_hidden', 'note_client', 'date_completion']
        widgets = {
            'whats_broken': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'whats_broken'}),
            'device_appearance': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'device_appearance'}),
            'device_type': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'device_type'}),
            'imei': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'imei'}),
            'device_brand': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'device_brand'}),
            'device_model': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'device_model'}),
            'device_kit': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'device_kit'}),
            'device_pass': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'device_pass'}),
            'price': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'price'}),
            'prepayment': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'prepayment'}),
            'repairer': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'repairer'}),
            'note_hidden': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'note_hidden'}),
            'note_client': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'note_client'}),
            'date_completion': forms.DateInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'date_completion'}), 
        }


class WorkForm(forms.ModelForm):
    class Meta:
        model = Works
        fields = ['work', 'price', 'cost', 'guarantee', 'discount', 'quantity', 'repairer']
        widgets = {
            'order': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'order'}),
            'work': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'work'}),
            'price': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'price'}),
            'cost': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'cost'}),
            'guarantee': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'guarantee'}),
            'discount': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'discount'}),
            'quantity': forms.NumberInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'quantity'}),
            'repairer': forms.TextInput(attrs={'class': 'text-field__input', 
                                                    'placeholder': 'repairer'}),
        }


class OrderHistoryForm(forms.ModelForm):
    class Meta:
        model = OrderHistory
        fields = ['message', ]
        widgets = {
            'message': forms.Textarea(attrs={'class': 'order_containers-history history_message',
                                             'rows': 5})
        }