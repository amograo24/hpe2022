from django import forms
from django.core.validators import MinLengthValidator


class RegisterForm(forms.Form):
    division = forms.ChoiceField(label="Choose any of the following that apply to you", choices=[
        ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
        ('I/SP', 'Insurance/Health Service Provider'),
        ('MSh', 'Medical Shop'),
        ('NoU', 'None of the Above')
    ], required=True)
    full_name = forms.CharField(label='Full Name', max_length=200, required=True)
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=True)
    reg_no = forms.CharField(max_length=20, label='Registration no.', required=True)
    aadharid = forms.CharField(max_length=12, label='Aadhar ID', required=True,
                               widget=forms.TextInput(attrs={"type": "number"}), validators=[MinLengthValidator(12)])
    department = forms.CharField(max_length=100, required=False)


class LoginForm(forms.Form):
    username = forms.CharField(label="WB ID/HCWV ID", max_length=16, validators=[MinLengthValidator(11)])
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

