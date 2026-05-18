from django.contrib.auth.forms import AuthenticationForm


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
