# Generated by Django 4.0.1 on 2022-02-06 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_usertype_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertype',
            name='svg_path',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
