from django.db import models

# Create your models here.

class DEPT(models.Model):
    code_dept = models.CharField(max_length=100, default='')
    name_dept = models.CharField(max_length=100, default='')
    def __str__(self):
        return str(self.code_dept) + " - " + str(self.name_dept)

class SEM(models.Model):
    code_sem = models.IntegerField(default='')
    after_sem = models.CharField(max_length=100, default='')
    def __str__(self):
        return str(self.code_sem) + " - " + str(self.after_sem)

class Student(models.Model):
    id_student = models.CharField(max_length=20, default='')
    full_name_student = models.CharField(max_length=100, default='')
    # name_class = models.CharField(max_length=20, default='')
    # email = models.EmailField(max_length = 254, default='')

    def __init__(seft, id_student, full_name_student):
        seft.id_student = id_student
        seft.full_name_student = full_name_student

    def __str__(self):
        return str(self.id_student) + " - " + str(self.full_name_student)

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    DEPT = models.ForeignKey(DEPT, on_delete=models.CASCADE)
    SEM = models.ForeignKey(SEM, on_delete=models.CASCADE)
    date = models.CharField(max_length=20, default='')
    time = models.CharField(max_length=20, default='')

    def __str__(seft):
        return str(self.Student) + str(self.DEPT) + str(self.SEM) + str(self.date)
