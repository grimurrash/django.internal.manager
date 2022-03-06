# Generated by Django 3.2.8 on 2021-11-07 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0009_auto_20211026_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='updated',
            field=models.DateField(blank=True, null=True, verbose_name='Время последнего изменения'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='actual_action',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Активное действие'),
        ),
    ]