from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from ecom.models import Customer, Order, Payment, FieldStaff
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'city', 'state', 'phone', 'field_staff']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{10,15}'}),
            'field_staff': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['field_staff'].queryset = FieldStaff.objects.all()
        self.fields['field_staff'].label_from_instance = lambda obj: f"{obj.userid.first_name} {obj.userid.last_name} - {obj.assigned_area}"

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }