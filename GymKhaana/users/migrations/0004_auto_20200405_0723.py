# Generated by Django 2.2.6 on 2020-04-05 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200401_1825'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='is_student',
            new_name='is_customer',
        ),
    ]
