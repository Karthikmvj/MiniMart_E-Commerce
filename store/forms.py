from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product, Review, OrderReturn, OrderCancellation, SavedSearch, Category, Brand, Color, ProductImage

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProductForm(forms.ModelForm):
    extra_images = MultipleFileField(
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}),
        required=False,
        help_text='Upload additional images for the product gallery.',
    )

    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'original_price', 'images', 'stock', 'is_available', 'is_featured', 'category', 'brand']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'style': 'margin-bottom: 15px;'}),
            'is_featured': forms.CheckboxInput(attrs={'style': 'margin-bottom: 15px;'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        original_price = cleaned_data.get('original_price')
        if price and original_price and original_price < price:
            self.add_error('original_price', "Original price cannot be lower than the sale price.")
        
        category = cleaned_data.get('category')
        if category and category.category_name.lower() in ['fruits', 'vegetables']:
            cleaned_data['brand'] = None
        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=commit)
        if commit:
            extra_images = self.cleaned_data.get('extra_images')
            if extra_images:
                for image in extra_images:
                    ProductImage.objects.create(product=product, image=image)
        return product

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'rating': forms.Select(attrs={'class': 'form-select'}, choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review...'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a CSV file to upload',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )


class ProductFilterForm(forms.Form):
    SORT_CHOICES = (
        ('', _('Sort by')),
        ('newest', _('Newest')),
        ('price_low', _('Price: Low to High')),
        ('price_high', _('Price: High to Low')),
        ('rating', _('Highest Rated')),
    )
    
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    brand = forms.ModelMultipleChoiceField(queryset=Brand.objects.all(), required=False, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Min Price')}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Max Price')}))
    rating = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}), choices=[
        ('', _('All Ratings')),
        ('4', _('4+ Stars')),
        ('3', _('3+ Stars')),
        ('2', _('2+ Stars')),
        ('1', _('1+ Stars')),
    ])
    sort = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}), choices=SORT_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        if min_price is not None and max_price is not None and min_price > max_price:
            self.add_error('max_price', "Max price cannot be lower than Min price.")
        return cleaned_data


class OrderReturnForm(forms.ModelForm):
    class Meta:
        model = OrderReturn
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please explain why you want to return this item'}),
        }


class OrderCancellationForm(forms.ModelForm):
    class Meta:
        model = OrderCancellation
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: Tell us why you want to cancel'}),
        }


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = ['query', 'category', 'min_price', 'max_price']
        widgets = {
            'query': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search term'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'min_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price'}),
            'max_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price'}),
        }
