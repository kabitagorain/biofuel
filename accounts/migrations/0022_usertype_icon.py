# Generated by Django 4.0.1 on 2022-02-24 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_remove_usertype_svg_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertype',
            name='icon',
            field=models.ImageField(default='', upload_to='usertype/'),
            preserve_default=False,
        ),
    ]
