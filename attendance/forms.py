from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm, AuthenticationForm
from django.db import transaction
from django.forms.utils import ValidationError
from attendance.models import User, Student, Teacher

from crispy_forms.layout import Layout, Field

class TeacherSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Tên của bạn'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Họ và tên lót'}))
    username = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Tên đăng nhập'}))
    email = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}))
    password1 = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Mật khẩu'}))
    password2 = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Xác nhận mật khẩu'}))
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields= ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        Teacher.objects.create(user=user, user_name=user.username, full_name_teacher=user.last_name + " " + user.first_name,  email=user.email)
        return user


class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Tên của bạn'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Họ và tên lót'}))
    username = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Mã số sinh viên'}))
    email = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email của bạn'}))
    class_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã lớp học'}))
    password1 = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Mật khẩu'}))
    password2 = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Xác nhận mật khẩu'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields= ['last_name', 'first_name', 'username', 'class_name', 'email']
    
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        Student.objects.create(user=user, id_student=user.username, full_name_student=user.last_name + " " + user.first_name, name_class=user.class_name, email=user.email)
        return user


class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Tên đăng nhập'}))
    password = forms.CharField(label="", max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Mật khẩu'}))
    class Meta:
        model = User
        fields= ['username','password']


class ContactForm(forms.Form):
    contact_name = forms.CharField(
        required=True, max_length=100, widget=forms.TextInput(attrs={'type': 'text', 'id': 'form-contact-name', 'class': "form-control", 'placeholder': 'Họ tên'}))
    contact_email = forms.EmailField(
        required=True, max_length=100, widget=forms.EmailInput(attrs={'class': "form-control", 'placeholder': 'Email'}))
    content = forms.CharField(required=True, widget=forms.Textarea(
        attrs={'type': 'textarea', 'id': "form-contact-message", 'class': "form-control md-textarea", 'rows': "4", 'placeholder': 'Lời nhắn'}))

    def __str__(seft):
        return str(self.contact_name) + "-" + str(self.contact_name) + " : " + str(self.content)


class UserUpdateForm(forms.ModelForm):

    email = forms.EmailField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Tên'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Họ và tên lót'}))
    class_name = forms.CharField(label="", max_length=10, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Mã lớp'}))
    class Meta:
        model = User
        fields = ['email', 'first_name','last_name', 'class_name']


class PasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')
    
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['old_password'].widget.attrs['placeholder'] = 'Mật khẩu cũ'
        self.fields['old_password'].label = ""
        
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Mật khẩu mới'
        self.fields['new_password1'].label = ""
        self.fields['new_password1'].help_text = '<span class="form-text text-muted"><small><ul style="list-style-type: none"><li>Mật khẩu không được chứa tên đăng nhập.</li><li>Mật khẩu của bạn phải chứa tối thiểu 8 kí tự.</li><li>Mật khẩu của bạn không được quá dễ đoán.</li><li>Mật khẩu phải chứa kí tự, số, và kí tự đặc biệt.</li></ul></small></span>'
        
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Xác nhận mật khẩu'
        self.fields['new_password2'].label = ""
        self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Hãy nhập lại đúng mật khẩu, trước khi đổi mật khẩu.</small></span>'
