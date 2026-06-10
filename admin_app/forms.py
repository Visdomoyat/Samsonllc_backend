from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from .models import Product, StackBlend

User = get_user_model()


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


class StackBlendForm(forms.ModelForm):
    class Meta:
        model = StackBlend
        fields = (
            'name',
            'kind',
            'image',
            'description',
            'price',
            'is_active',
            'display_order',
        )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Stack or blend name',
            }),
            'kind': forms.Select(attrs={'class': 'form-input'}),
            'image': forms.FileInput(attrs={'class': 'form-input-file'}),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Description for the storefront',
                'rows': 4,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0',
                'step': '1',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['image'].required = False


class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'autocomplete': 'username',
        })

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if (
            User.objects.exclude(pk=self.instance.pk)
            .filter(username__iexact=username)
            .exists()
        ):
            raise forms.ValidationError('That username is already taken.')
        return username


class AccountPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, autocomplete in (
            ('old_password', 'current-password'),
            ('new_password1', 'new-password'),
            ('new_password2', 'new-password'),
        ):
            self.fields[field_name].widget.attrs.update({
                'class': 'form-input',
                'autocomplete': autocomplete,
            })
