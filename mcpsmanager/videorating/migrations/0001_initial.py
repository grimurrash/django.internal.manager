# Generated by Django 4.0.4 on 2023-02-04 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255, verbose_name='Тип учатсника')),
                ('school', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Наименование школы')),
                ('team_name', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Наименование отряда')),
                ('video_url', models.CharField(blank=True, default=None, max_length=2000, null=True, verbose_name='Видео ссылка')),
                ('leader_fio', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Руководитель ФИО')),
                ('reference_url', models.CharField(blank=True, default=None, max_length=2000, null=True, verbose_name='Справка ссылка')),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участник',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appraiser', models.CharField(max_length=255, verbose_name='Оценщик')),
                ('points', models.FloatField(verbose_name='Баллов')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videorating.participant', verbose_name='Участник')),
            ],
            options={
                'verbose_name': 'Оценка',
                'verbose_name_plural': 'Оценка',
                'ordering': ['-id'],
            },
        ),
    ]