from django import forms
from .models import *



class ClientForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['source'].empty_label = 'Источник не выбран'
    source = forms.ModelChoiceField(queryset=ClientSource.objects.all(), label='Источник',
                                    empty_label='Выберите источник', widget=forms.Select(
                                        attrs={'class': 'text-field__input',
                                        'placeholder': 'source'}))

    class Meta:
        model = Client
        fields = ['name', 'tel', 'email', 'source', 'adress', 'comment_client']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'text-field__input', 
                                            'placeholder': 'name'}),
            'tel': forms.TextInput(attrs={'class': 'text-field__input', 
                                            'placeholder': 'tel',
                                            'type': 'tel',
                                            'pattern': "\+[7][0-9]{10}"}),
            'email': forms.EmailInput(attrs={'class': 'text-field__input', 
                                            'placeholder': 'email'}),
            'source': forms.Select(attrs={'class': 'text-field__input',
                                                    'placeholder': 'Источник'}), 
            'adress': forms.TextInput(attrs={'class': 'text-field__input', 
                                            'placeholder': 'adress'}),
            'comment_client': forms.TextInput(attrs={'class': 'text-field__input', 
                                            'placeholder': 'comment_client'})
        }