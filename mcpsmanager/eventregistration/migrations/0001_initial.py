# Generated by Django 4.0.4 on 2022-05-20 03:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgeGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('min', models.PositiveIntegerField(verbose_name='Минимальный возраст')),
                ('max', models.PositiveIntegerField(verbose_name='Максимальный возраст')),
            ],
            options={
                'verbose_name': 'Возрастная группа',
                'verbose_name_plural': 'Возрастная группы',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Направление',
                'verbose_name_plural': 'Направления',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('slug', models.CharField(max_length=255, verbose_name='Анг наименование (используется для ссылки)')),
                ('limit_for_one_user', models.PositiveIntegerField(default=100, verbose_name='Лимит регистраций для одного пользователя')),
                ('is_save_google_table', models.BooleanField(default=False, verbose_name='Сохранять в гугл таблице')),
                ('google_spreadsheet_id', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Гугл таблица')),
                ('is_send_registration_mail_notification', models.BooleanField(default=False, verbose_name='Отправлять письмо о регистрации')),
                ('from_email_address', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Почта для рассылок')),
                ('registration_mail_subject', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Тема письма о регистрации')),
                ('registration_mail_text', models.TextField(blank=True, default=None, null=True, verbose_name='Текст письма о регистрации')),
                ('reminder_mail_text', models.TextField(blank=True, default=None, null=True, verbose_name='Текст письма с напоминанием')),
                ('is_save_documents', models.BooleanField(default=False, verbose_name='Сохранять файлы в папке')),
                ('document_save_folder_id', models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Папка для сохранения файлов')),
                ('support_email_address', models.CharField(max_length=255, verbose_name='Почта поддержки')),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятие',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('shift_date', models.DateTimeField(verbose_name='Дата начала')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventregistration.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Смена',
                'verbose_name_plural': 'Смены',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=100, verbose_name='Отчество')),
                ('date_of_birth', models.DateField(verbose_name='Дата рождения')),
                ('email', models.CharField(max_length=100, verbose_name='Электронная почта')),
                ('additionally_data', models.JSONField(blank=True, default=None, null=True, verbose_name='Дополнительная информация')),
                ('is_send_registration_mail', models.BooleanField(default=False, verbose_name='Было ли отправлено письмо о регистрации')),
                ('is_send_reminder_mail', models.BooleanField(default=False, verbose_name='Было ли отправлено письмо с напоминанием')),
                ('age_group', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eventregistration.agegroup', verbose_name='Смена')),
                ('direction', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eventregistration.direction', verbose_name='Смена')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventregistration.event', verbose_name='Мероприятие')),
                ('shift', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eventregistration.shift', verbose_name='Смена')),
            ],
            options={
                'verbose_name': 'Регистрация участников',
                'verbose_name_plural': 'Регистрация участников',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='EventLimit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limit', models.PositiveIntegerField(default=10000, verbose_name='Максимальное кол-во')),
                ('free_seats', models.PositiveIntegerField(default=10000, verbose_name='Осталось мест')),
                ('age_group', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eventregistration.agegroup', verbose_name='Возрастная группа')),
                ('direction', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eventregistration.direction', verbose_name='Направление')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventregistration.event', verbose_name='Мероприятие')),
                ('shift', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eventregistration.shift', verbose_name='Смена')),
            ],
            options={
                'verbose_name': 'Ограничения кол-ва',
                'verbose_name_plural': 'Ограничение кол-ва',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('btn_name', models.CharField(default='', max_length=255, verbose_name='Текст в кнопке')),
                ('checkbox_text', models.CharField(default='', max_length=255, verbose_name='Текст чекбокса')),
                ('file', models.FileField(upload_to='uploads/documents/%Y/%m/%d/')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventregistration.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документы',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='direction',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventregistration.event', verbose_name='Мероприятие'),
        ),
        migrations.AddField(
            model_name='agegroup',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventregistration.event', verbose_name='Мероприятие'),
        ),
    ]
