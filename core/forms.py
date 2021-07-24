from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class CheckkOutForm(forms.Form):
    
    street_adress = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : '1234 Main St'
    }))
    apartment_adress = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder' : 'Orzechowa'
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class' : 'custom-select d-block w-100'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))
    same_shipping_adress = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):

    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': "Recipient\'s username",
        'aria-describedby': "basic-addon2"
    }))