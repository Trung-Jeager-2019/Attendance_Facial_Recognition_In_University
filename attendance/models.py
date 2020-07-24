from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe


class User(AbstractUser):
    class_name = models.CharField(max_length=10, default="")
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    id_student = models.CharField(max_length=20, default='')
    full_name_student = models.CharField(max_length=100, default='')
    name_class = models.CharField(max_length=20, default='')
    email = models.EmailField(max_length = 254, default='')

    def __str__(self):
        return self.user.username + " - " + self.user.last_name + " " + self.user.first_name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_name = models.CharField(max_length=20, default='')
    full_name_teacher = models.CharField(max_length=100, default='')
    email = models.EmailField(max_length = 254, default='')

    def __str__(self):
        return self.user.username + " - " + self.user.last_name + " " + self.user.first_name

class DEPT(models.Model):
    code_dept = models.CharField(max_length=100, default='')
    name_dept = models.CharField(max_length=100, default='')

    def __str__(self):
        return (str(self.code_dept) + " - " + str(self.name_dept))

class SEM(models.Model):
    code_sem = models.IntegerField(default='')
    after_sem = models.CharField(max_length=100, default='')

    def __str__(self):
        return (str(self.code_sem) + " - " + str(self.after_sem))


class Attendance(models.Model):
    # id = models.AutoField(primary_key=True)
    id_student = models.CharField(max_length=100, default='')
    DEPT = models.CharField(max_length=100, default='')
    SEM = models.IntegerField(default='')
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return (str(self.id_student) + " - " + str(self.DEPT) + " - " + str(self.SEM) + " - " + str(self.date) + " - " + str(self.time))
