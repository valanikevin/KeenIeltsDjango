from django import forms

class RegistrationForm(forms.ModelForm):
    class Meta:
        fields = ['first_name', 'last_name', 'email', 'password']
