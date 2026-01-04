from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from journal.models import JournalEntry

# Shared Tailwind CSS classes for form inputs
FORM_INPUT_CLASSES = (
    "w-full px-4 py-3 border border-gray-300 rounded-lg "
    "focus:ring-2 focus:ring-blue-500 focus:border-transparent"
)

TEXTAREA_CLASSES = f"{FORM_INPUT_CLASSES} resize-none"


class CustomLoginForm(AuthenticationForm):
    """Custom login form with Tailwind styling."""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": FORM_INPUT_CLASSES,
                "placeholder": "Username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": FORM_INPUT_CLASSES,
                "placeholder": "Password",
            }
        )
    )


class CustomRegisterForm(UserCreationForm):
    """Custom registration form with Tailwind styling."""

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["username", "password1", "password2"]:
            self.fields[field_name].widget.attrs.update(
                {
                    "class": FORM_INPUT_CLASSES,
                    "placeholder": self.fields[field_name].label or field_name.title(),
                }
            )


class JournalEntryForm(forms.ModelForm):
    """Form for creating journal entries."""

    class Meta:
        model = JournalEntry
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASSES,
                    "rows": 6,
                    "placeholder": "Write your thoughts...",
                }
            )
        }
        labels = {
            "content": "",
        }
