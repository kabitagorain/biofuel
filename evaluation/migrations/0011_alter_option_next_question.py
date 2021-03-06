# Generated by Django 4.0.1 on 2022-02-11 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0010_alter_question_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='next_question',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next_question', to='evaluation.question'),
        ),
    ]
