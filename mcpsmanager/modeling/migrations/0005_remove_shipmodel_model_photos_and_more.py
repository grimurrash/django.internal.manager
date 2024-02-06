# Generated by Django 4.0.4 on 2023-09-25 21:00

from django.db import migrations, models
import django.db.models.deletion
import modeling.models


class Migration(migrations.Migration):

    dependencies = [
        ('modeling', '0004_alter_shipmodel_model_drawing_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shipmodel',
            name='model_photos',
        ),
        migrations.AlterField(
            model_name='shipmodel',
            name='main_photo',
            field=models.FileField(blank=True, default=None, null=True, upload_to=modeling.models.ship_model_path, verbose_name='Основное фото'),
        ),
        migrations.AlterField(
            model_name='shipmodel',
            name='model_drawing',
            field=models.FileField(blank=True, default=None, null=True, upload_to=modeling.models.ship_model_path, verbose_name='Чертёж модели'),
        ),
        migrations.AlterField(
            model_name='shipmodel',
            name='model_passport',
            field=models.FileField(blank=True, default=None, null=True, upload_to=modeling.models.ship_model_path, verbose_name='Паспорт модели'),
        ),
        migrations.CreateModel(
            name='ShipModelFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=modeling.models.ship_model_file_path)),
                ('ship_model_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modeling.shipmodel', verbose_name='Модель')),
            ],
        ),
    ]
