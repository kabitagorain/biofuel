# Generated by Django 4.0.1 on 2022-02-24 11:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_usertype_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertype',
            name='svg_path',
        ),
    ]
