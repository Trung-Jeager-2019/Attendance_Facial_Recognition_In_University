# Generated by Django 3.0.5 on 2020-06-19 06:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_user_class_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('user_name', models.CharField(default='', max_length=20)),
                ('full_name_teacher', models.CharField(default='', max_length=100)),
                ('email', models.EmailField(default='', max_length=254)),
            ],
        ),
    ]
