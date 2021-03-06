# Generated by Django 3.2.8 on 2021-10-26 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0007_auto_20211021_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='actual_action',
            field=models.CharField(default='', max_length=50, null=True, verbose_name='Активное действие'),
        ),
        migrations.AlterField(
            model_name='account',
            name='employees',
            field=models.ManyToManyField(blank=True, related_name='favorite_accounts', to='helpdesk.Employee'),
        ),
        migrations.AlterField(
            model_name='account',
            name='password',
            field=models.CharField(blank=True, max_length=100, verbose_name='Пароль'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='is_send_report',
            field=models.BooleanField(default=False, verbose_name='Отправлять уведомления'),
        ),
    ]
