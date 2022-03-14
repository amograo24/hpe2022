from django import forms
from django.core.validators import MinLengthValidator
# from .models import HealthStatus,HealthValue,Files
from .models import Files



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

# class UploadDocForm(forms.Form):
#     patient = forms.CharField(max_length=16,label="Patient's WBID",required=True,widget=forms.TextInput(attrs={"type":"number"}),validators=[MinLengthValidator(16)])
#     vendor_name = form.CharField(max_length=200,label="Name of person uploading this document",required=False)

class UploadDocForm(forms.Form):
    patient = forms.CharField(max_length=16,label="Patient's WBID",required=True,widget=forms.TextInput(attrs={"type":"number"}),validators=[MinLengthValidator(16)])
    vendor_name = forms.CharField(max_length=200,label="Name of person uploading this document",required=True)
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),required=False)
    file_type = forms.ChoiceField(label="File Type", choices=[
        ('PRSCN', 'Prescription'),
        ('S/T', 'Schedule/Timetable'),
        ('HR/TR', 'Health Report/Test Report'),
        ('INVCE', 'Invoice'),
        ('OP','Operative Report'),
        ('DS','Discharge Summary'),
        ('MSC','Miscellaneous')
    ], required=True)
    tags = forms.CharField(max_length=200,label="Tags/Keywords",required=False)

class EditFileForm(forms.ModelForm):
    class Meta:
        model=Files
        fields=['tags','vendor_name','file_type']
    # file_type = forms.CharField

class GoPublicForm(forms.Form):
    address = forms.CharField(max_length=500,label="Address",required=True)
    city = forms.CharField(max_length=30,label="City/Town",required=True)
    pincode = forms.CharField(max_length=6,label="Pincode",required=True,widget=forms.TextInput(attrs={"type":"number"}),validators=[MinLengthValidator(6)])
# class CreateHealthStatus(forms.ModelForm):
#     class Meta:
#         model=HealthStatus
#         fields=['patient','health_status','health_condition','maximum_value','minimum_value','patient_value']



