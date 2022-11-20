# Generated by Django 4.0.4 on 2022-11-20 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botadvisors', '0005_interview_delete_userquestionslist'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='google_table_row',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Строка в гугл таблице'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='interview_answers',
            field=models.JSONField(default=dict, verbose_name='Ответы опроса'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='step',
            field=models.CharField(default='start', max_length=100, verbose_name='Этап опроса'),
        ),
    ]
