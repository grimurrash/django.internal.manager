# Generated by Django 4.0.4 on 2023-02-14 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videorating', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='comment',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Комментарий'),
        ),
    ]