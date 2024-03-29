from django import forms
from django.core.validators import MinLengthValidator
from .models import Files


class RegisterForm(forms.Form):
    division = forms.ChoiceField(label="Choose any of the following that applies to you", choices=[
        ('D/HCW/MS', 'Doctor/Health Care Worker/Medical Staff'),
        ('I/SP', 'Insurance/Health Service Provider'),
        ('MSh', 'Medical Shop/Lab'),
        ('NoU', 'None of the Above')
    ], required=True)
    full_name = forms.CharField(label='Full Name', max_length=40, required=True)
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=True)
    reg_no = forms.CharField(max_length=20, label='Registration no./License ID', required=True)
    aadharid = forms.CharField(max_length=12, label='Aadhar ID', required=True,
                               widget=forms.TextInput(attrs={"type": "number"}), validators=[MinLengthValidator(12)])
    department = forms.CharField(max_length=60, required=False)


class LoginForm(forms.Form):
    username = forms.CharField(label="WB ID/HCWV ID", max_length=16, validators=[MinLengthValidator(11)])
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)


class UploadDocForm(forms.Form):
    patient = forms.CharField(max_length=16, label="Patient's WBID", required=True,
                              widget=forms.TextInput(attrs={"type": "number"}), validators=[MinLengthValidator(16)])
    vendor_name = forms.CharField(max_length=40, label="Name of person uploading this document", required=True)
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    file_type = forms.ChoiceField(label="File Type", choices=[
        ('PRSCN', 'Prescription'),
        ('S/T', 'Schedule/Timetable'),
        ('HR/TR', 'Health Report/Test Report'),
        ('INVCE', 'Invoice'),
        ('OP', 'Operative Report'),
        ('DS', 'Discharge Summary'),
        ('MSC', 'Miscellaneous')
    ], required=True)
    tags = forms.CharField(max_length=200, label="Tags/Keywords", required=False)


class EditFileForm(forms.ModelForm):
    class Meta:
        model = Files
        fields = ['tags', 'vendor_name', 'file_type']


class GoPublicForm(forms.Form):
    contact_number = forms.CharField(max_length=10, label="Contact Number", required=True,
                              widget=forms.TextInput(attrs={"type": "number"}), validators=[MinLengthValidator(10)])    
    address = forms.CharField(max_length=300, label="Address", required=True)
    pincode = forms.CharField(max_length=6, label="Pincode", required=True,
                              widget=forms.TextInput(attrs={"type": "number"}), validators=[MinLengthValidator(6)])

