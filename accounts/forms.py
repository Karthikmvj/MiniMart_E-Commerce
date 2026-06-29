from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Address, PaymentMethod, NotificationPreference
from django.utils.translation import gettext_lazy as _

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': _('Enter Password'),
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': _('Confirm Password'),
        'class': 'form-control',
    }))
    name = forms.CharField(max_length=100, label=_('Full Name'), widget=forms.TextInput(attrs={
        'placeholder': _('Full Name'),
        'class': 'form-control',
    }))
    mobile_number = forms.CharField(max_length=15, required=False, label=_('Mobile Number'), widget=forms.TextInput(attrs={
        'placeholder': _('Mobile Number'),
        'class': 'form-control',
    }))

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'mobile_number', 'password']
        labels = {'username': _('Username'), 'email': _('Email Address')}
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': _('Username'), 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': _('Email Address'), 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match!"))
            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        name = self.cleaned_data.get('name')
        if name:
            parts = name.split(maxsplit=1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                mobile_number=self.cleaned_data.get('mobile_number', '')
            )
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('user', 'created_at')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Full Name')}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Phone Number')}),
            'address_type': forms.Select(attrs={'class': 'form-select'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Address Line 1')}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Address Line 2 (Optional)')}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('City')}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('State')}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Postal Code')}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Country')}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'card_number', 'card_holder_name', 'expiry_date', 'upi_id', 'is_default']
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Card Number')}),
            'card_holder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Card Holder Name')}),
            'expiry_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('UPI ID')}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        exclude = ('user', 'created_at')
        widgets = {
            field.name: forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'style': 'margin-left: 0; cursor: pointer;'})
            for field in NotificationPreference._meta.fields
            if isinstance(field, forms.BooleanField)
        }