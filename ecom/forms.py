from django import forms
from .models import SiteVisit, FieldStaff,Customer
from django import forms
from django.contrib.auth.models import User
from .models import FieldStaff
from django.db import models
from django import forms
from .models import  Order

from django.contrib.auth.forms import UserCreationForm
class CustomerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
                                                                                                                
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
class CustomerUpdateForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your address'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your city'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your state'
        })
    )
    
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'city', 'state']
        exclude = ['userid', 'customer_type', 'approched_by_staff']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Validate phone number (basic validation)
        if not phone.isdigit():
            raise forms.ValidationError('Phone number should contain only digits.')
        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError('Phone number should be between 10 and 15 digits.')
        return phone

class FieldStaffUpdateForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your address',
            'rows': 3
        })
    )
    class Meta:
        model = FieldStaff
        fields = ['phone','address']
        exclude = ['base_salary', 'incentive_percentage', 'join_date', 'userid', 'assigned_area']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Validate phone number (basic validation)
        if not phone.isdigit():
            raise forms.ValidationError('Phone number should contain only digits.')
        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError('Phone number should be between 10 and 15 digits.')
        return phone



class SiteVisitForm(forms.ModelForm):
    class Meta:
        model = SiteVisit
        exclude = ['field_staff']  # Exclude field_staff from the form
        widgets = {
            'visit_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'proposed_date_visit': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'comments': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'large_project': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'site_address': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'city': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'type': 'tel'}
            ),
            'square_feet': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),
            'stage_of_construction': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'owner_name': forms.TextInput(  
                attrs={'class': 'form-control'}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(str(phone)) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits")
        return phone

    def clean_square_feet(self):
        square_feet = self.cleaned_data.get('square_feet')
        if square_feet and square_feet <= 0:
            raise forms.ValidationError("Square feet must be greater than 0")
        return square_feet

# Add these imports at the top of your views.py file
# forms.py


class OrderAssignmentForm(forms.Form):
    field_staff = forms.ModelChoiceField(
        queryset=FieldStaff.objects.all(),
        empty_label="Select a field staff",
        label="Field Staff",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)
        
        # If we have a customer address, try to match field staff by area
        if order and order.customer and order.customer.city:
            customer_city = order.customer.city.lower()
            # Order field staff by matching area to customer city for convenience
            self.fields['field_staff'].queryset = FieldStaff.objects.all().order_by(
                # Put field staff with matching area first
                ~models.Q(assigned_area__icontains=customer_city),
                'assigned_area'
            )

from django import forms
from .models import tbl_review

class ReviewForm(forms.ModelForm):
    """Form for submitting product reviews with images"""
    rating = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'id': 'id_rating'}),
        min_value=1,
        max_value=5
    )
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'id_title', 'placeholder': 'Review Title'}
        )
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'id': 'id_comment', 'rows': '4', 
                  'placeholder': 'Share your thoughts about this product...'}
        )
    )
    image1 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    image2 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    image3 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    class Meta:
        model = tbl_review
        fields = ['rating', 'title', 'comment', 'image1', 'image2', 'image3']