# Generated by Django 3.2.7 on 2021-10-01 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0002_auto_20210929_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_send_report',
            field=models.BooleanField(default=False, verbose_name='Отправлять отчеты по заявкам по времени'),
        ),
    ]