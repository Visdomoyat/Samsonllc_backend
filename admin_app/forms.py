from django import forms

from django.contrib.auth.forms import AuthenticationForm

from .models import Product


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, placeholder in (
            ('username', 'Username'),
            ('password', 'Password'),
        ):
            self.fields[field_name].widget.attrs.update({
                'class': 'form-input',
                'placeholder': placeholder,
                'autocomplete': 'username' if field_name == 'username' else 'current-password',
            })


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'image', 'description', 'price')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product name'}),
            'image': forms.FileInput(attrs={'class': 'form-input-file'}),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Product description',
                'rows': 4,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['image'].required = False
