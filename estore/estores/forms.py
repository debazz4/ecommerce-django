from dataclasses import field
from pyexpat import model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import clear_script_prefix
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            'type':"text",
            'class':"form-control",
            'id':"username",
            'name':"username",
            'required':'',
		})
        self.fields["email"].widget.attrs.update({
            'type':"email",
            'class':"form-control",
            'id':"register-email-1",
            'name':"register-email",
            'required':'',
		})
        self.fields["password1"].widget.attrs.update({
            'type':"password", 
            'class':"form-control", 
            'id':"register-password-1",
            'name':"register-password",
            'required':"",					    		
        })
        self.fields["password2"].widget.attrs.update({
            'type':"password", 
            'class':"form-control", 
            'id':"register-password-2",
            'name':"register-password",
            'required':"",					    		
        })

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'House number and Street name',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Appartments, suite, unit etc ...',
        'class': 'form-control'
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'form-control'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    state = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    
