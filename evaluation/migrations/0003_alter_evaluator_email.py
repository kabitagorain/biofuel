# Generated by Django 4.0.1 on 2022-02-02 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0002_alter_evalebelstatement_evaluator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluator',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]