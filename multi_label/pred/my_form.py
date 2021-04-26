from django import forms
from django.core.exceptions import ValidationError
from pred import models
import hashlib


def getMd5Passwd(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()


class UploadImageForm(forms.Form):
    patient_id = forms.CharField(label="患者id")
    patient_name = forms.CharField(label="患者姓名")
    img_type = forms.ChoiceField(label="影像类别", choices=(("OCT", "OCT"), ("fundus", "fundus")))
    note = forms.CharField(label="备注", required=False)
    photo = forms.ImageField(label='请上传一张影像:')


class UserRegisterForm(forms.Form):
    user_name = forms.CharField(min_length=3, label="用户名")
    password = forms.CharField(min_length=6, label="输入密码", widget=forms.PasswordInput())
    repeat_password = forms.CharField(min_length=6, label="重复密码", widget=forms.PasswordInput())

    def clean(self):
        is_username_exist = models.User.objects.filter(user_name=self.cleaned_data.get('user_name')).exists()
        if is_username_exist:
            raise ValidationError('该用户名已被注册')
        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password'):
            raise ValidationError('密码不一致')
        else:
            return self.cleaned_data


class UserLoginForm(forms.Form):
    user_name = forms.CharField(min_length=3, label="用户名")
    password = forms.CharField(min_length=6, label="密码", widget=forms.PasswordInput())

    def clean(self):
        password = models.User.objects.get(user_name=self.cleaned_data.get('user_name')).password
        if getMd5Passwd(self.cleaned_data.get('password')) != password:
            raise ValidationError('密码错误')
        else:
            return self.cleaned_data


class UserChangePasswdForm(forms.Form):
    old_passwd = forms.CharField(min_length=6, label="旧密码", widget=forms.PasswordInput())
    new_passwd = forms.CharField(min_length=6, label="新密码", widget=forms.PasswordInput())
    repeat_new_passwd = forms.CharField(min_length=6, label="重复新密码", widget=forms.PasswordInput())

    def clean(self):
        if self.cleaned_data.get('new_passwd') != self.cleaned_data.get('repeat_new_passwd'):
            raise ValidationError('新密码不一致')
        else:
            return self.cleaned_data
