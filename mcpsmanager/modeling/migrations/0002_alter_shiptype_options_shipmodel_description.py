# Generated by Django 4.0.4 on 2022-11-15 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modeling', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shiptype',
            options={'ordering': ['id'], 'verbose_name': 'Класс моделей судов', 'verbose_name_plural': 'Классы моделей судов'},
        ),
        migrations.AddField(
            model_name='shipmodel',
            name='description',
            field=models.TextField(default='', verbose_name='Описание'),
        ),
    ]
