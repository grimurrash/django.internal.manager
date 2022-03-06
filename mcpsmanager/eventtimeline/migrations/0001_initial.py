# Generated by Django 3.2.8 on 2021-12-02 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TimelineEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=255, verbose_name='Наименование события')),
                ('description', models.TextField(verbose_name='Основной текст')),
                ('event_date', models.DateField(verbose_name='Дата события')),
                ('images', models.TextField(blank=True, null=True, verbose_name='Ссылки на изображения')),
                ('video', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ссылка на видео')),
                ('tags', models.CharField(blank=True, max_length=255, null=True, verbose_name='Теги (через запятую)')),
            ],
            options={
                'verbose_name': 'Событие',
                'verbose_name_plural': 'События',
                'ordering': ['-id'],
            },
        ),
    ]
