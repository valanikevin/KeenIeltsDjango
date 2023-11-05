from django import forms
from custom_user.models import User
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

import unicodedata
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', "email",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user


class AccountSettingForm(forms.ModelForm):
    testType = forms.ChoiceField(
        choices=[('academic', 'Academic'), ('general', 'General')],
        required=True
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name')  # Do not include testType here

    def save(self, commit=True):
        user = super(AccountSettingForm, self).save(commit=False)
        data = self.cleaned_data
        
        user.student.type = data['testType']
        if commit:
            user.student.save()
            user.save()
        return user

