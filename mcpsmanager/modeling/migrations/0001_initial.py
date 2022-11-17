# Generated by Django 4.0.4 on 2022-11-13 22:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShipType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Класс моделей судов',
                'verbose_name_plural': 'Классы моделей судов',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ShipModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=255, verbose_name='Название модели')),
                ('model_scale', models.CharField(max_length=255, verbose_name='Маштаб модели')),
                ('status', models.IntegerField(choices=[(0, 'На модерации'), (1, 'Принят'), (2, 'Не принят')], default=0)),
                ('surname', models.CharField(max_length=100, verbose_name='Имя')),
                ('first_name', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('last_name', models.CharField(max_length=100, verbose_name='Отчество')),
                ('date_of_birth', models.DateField(verbose_name='Дата рождения')),
                ('educational_organization', models.CharField(max_length=255, verbose_name='Образовательная организация')),
                ('email', models.CharField(max_length=100, verbose_name='Электронная почта')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Телефон')),
                ('zip_code', models.CharField(max_length=20, verbose_name='Почтовый год')),
                ('city_country', models.CharField(max_length=255, verbose_name='Город/страна')),
                ('actual_address', models.CharField(max_length=255, verbose_name='Фактический адрес')),
                ('model_passport', models.CharField(max_length=255, verbose_name='Паспорт модели')),
                ('model_drawing', models.CharField(max_length=255, verbose_name='Чертёж модели')),
                ('main_photo', models.CharField(max_length=255, null=True, verbose_name='Основное фото')),
                ('model_photos', models.JSONField(blank=True, default=None, null=True, verbose_name='Фотографии модели')),
                ('model_type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='modeling.shiptype', verbose_name='Класс модели')),
            ],
            options={
                'verbose_name': 'Модел судна',
                'verbose_name_plural': 'Модели судов',
                'ordering': ['-id'],
            },
        ),
    ]