from django import forms
from store.models import Product, Category, Offer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
from .models import SystemSettings

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['colors', 'price']
        labels = {
            'original_price': 'Price',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        product_name = cleaned_data.get('product_name')
        if not slug and product_name:
            cleaned_data['slug'] = slugify(product_name)
        
        category = cleaned_data.get('category')
        if category and category.category_name.lower() in ['fruits', 'vegetables']:
            cleaned_data['brand'] = None
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug and instance.product_name:
            instance.slug = slugify(instance.product_name)
            
        if instance.original_price is not None:
            instance.price = instance.original_price
        else:
            instance.price = 0
            
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description', 'category_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        category_name = cleaned_data.get('category_name')
        if not slug and category_name:
            cleaned_data['slug'] = slugify(category_name)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug and instance.category_name:
            instance.slug = slugify(instance.category_name)
        if commit:
            instance.save()
        return instance

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class AdminSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        if 'password1' in self.fields:
            self.fields['password1'].help_text = "Enter a password."

    def clean_password1(self):
        # Override to accept any password without Django validation
        return self.cleaned_data.get("password1")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'description', 'discount_percentage', 'start_date', 'end_date', 'active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

