# Generated by Django 3.2.8 on 2021-10-21 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0005_auto_20211020_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения'),
        ),
    ]