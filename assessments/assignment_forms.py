
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class StudentAssignmentForm(forms.Form):

    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(
            is_active=True,
            is_staff=False,
            is_superuser=False
        ).order_by("username"),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Students"
    )
