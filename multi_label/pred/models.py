from django.db import models


# Create your models here.

class History(models.Model):
    patient_id = models.CharField(max_length=20)
    patient_name = models.CharField(max_length=20)
    img_type = models.CharField(max_length=20)
    photo = models.ImageField()
    pred_result = models.CharField(max_length=100)
    note = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(to='User', on_delete=models.CASCADE)
    pred_time = models.DateTimeField(auto_now_add=True)


class User(models.Model):
    user_name = models.CharField(max_length=20)
    password = models.CharField(max_length=32)
