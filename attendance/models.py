from django.db import models

# Create your models here.

class DEPT(models.Model):

    dept = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.dept
