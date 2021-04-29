from django import forms
from django.core.exceptions import ValidationError
from pred import models
import hashlib


def getMd5Passwd(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()


class UploadImageForm(forms.Form):
    patient_id = forms.CharField(label="患者id",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入患者id'}))
    patient_name = forms.CharField(label="患者姓名",
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入患者姓名'}))
    img_type = forms.ChoiceField(label="影像类别", choices=(("OCT", "OCT"), ("fundus", "fundus")),
                                 widget=forms.RadioSelect())
    photo = forms.ImageField(label='上传一张影像')
    note = forms.CharField(label="备注", required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '备注（可为空）'}))


class UserRegisterForm(forms.Form):
    user_name = forms.CharField(min_length=3, label="用户名",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入用户名'}))
    password = forms.CharField(min_length=6, label="密码",
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '输入密码'}))
    repeat_password = forms.CharField(min_length=6, label="重复密码", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '再次输入用户名'}))

    def clean(self):
        is_username_exist = models.User.objects.filter(user_name=self.cleaned_data.get('user_name')).exists()
        if is_username_exist:
            raise ValidationError('该用户名已被注册')
        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password'):
            raise ValidationError('密码不一致')
        else:
            return self.cleaned_data


class UserLoginForm(forms.Form):
    user_name = forms.CharField(min_length=3, label="用户名",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入用户名'}))
    password = forms.CharField(min_length=6, label="密码",
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '输入密码'}))

    def clean(self):
        user_filter = models.User.objects.filter(user_name=self.cleaned_data.get('user_name'))
        if len(user_filter) == 0:
            raise ValidationError('用户不存在')
        password = user_filter[0].password
        if getMd5Passwd(self.cleaned_data.get('password')) != password:
            raise ValidationError('密码错误')
        else:
            return self.cleaned_data


class UserChangePasswdForm(forms.Form):
    old_passwd = forms.CharField(min_length=6, label="旧密码",
                                 widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '输入旧密码'}))
    new_passwd = forms.CharField(min_length=6, label="新密码",
                                 widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '输入新密码'}))
    repeat_new_passwd = forms.CharField(min_length=6, label="重复新密码", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '再次输入新密码'}))

    def clean(self):
        if self.cleaned_data.get('new_passwd') != self.cleaned_data.get('repeat_new_passwd'):
            raise ValidationError('新密码不一致')
        else:
            return self.cleaned_data
