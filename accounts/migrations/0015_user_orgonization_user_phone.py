# Generated by Django 4.0.1 on 2022-02-06 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_usertype_svg_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='orgonization',
            field=models.CharField(blank=True, max_length=252, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=252, null=True),
        ),
    ]
