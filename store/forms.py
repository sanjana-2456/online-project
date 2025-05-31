from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white'
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 3,
        'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white'
    }))
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'phone']
