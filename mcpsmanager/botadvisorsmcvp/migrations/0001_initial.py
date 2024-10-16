# Generated by Django 4.0.4 on 2024-10-14 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=100, verbose_name='Chat id')),
                ('step', models.CharField(default='start', max_length=100, verbose_name='Этап опроса')),
                ('interview_answers', models.JSONField(default=dict, verbose_name='Ответы опроса')),
                ('google_table_row', models.IntegerField(blank=True, default=None, null=True, verbose_name='Строка в гугл таблице')),
                ('test_finish_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Время окончания теста')),
                ('questing_text', models.JSONField(null=True, verbose_name='Вопросы')),
                ('questing_step', models.IntegerField(default=-1, verbose_name='Актуальный вопрос')),
                ('questing_balls', models.IntegerField(default=0, verbose_name='Кол-во балов')),
                ('is_need_send', models.BooleanField(default=0, verbose_name='Нужно ли отправлять сообщение')),
                ('is_send_final_message', models.BooleanField(default=0, verbose_name='Отправлено последнее сообщение')),
                ('video_url', models.CharField(default=None, max_length=2000, null=True, verbose_name='Ссылка на видео')),
                ('start_input_interview', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Время начала заполнения анкеты')),
                ('start_bot_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Время запуска бота')),
                ('test_try_count', models.IntegerField(default=0, verbose_name='Кол-во попыток пройти тест')),
            ],
            options={
                'verbose_name': 'Тестирование пользователя',
                'verbose_name_plural': 'Тестирование пользователя',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('questing_id', models.IntegerField(verbose_name='Номер вопроса')),
                ('block_name', models.CharField(max_length=100, verbose_name='Блок')),
                ('questing_text', models.TextField(verbose_name='Вопрос')),
                ('answer_one_text', models.TextField(blank=True, null=True, verbose_name='Ответ 1')),
                ('answer_one_balls', models.IntegerField(blank=True, null=True, verbose_name='Баллы за ответ 1')),
                ('answer_two_text', models.TextField(blank=True, null=True, verbose_name='Ответ 2')),
                ('answer_two_balls', models.IntegerField(blank=True, null=True, verbose_name='Баллы за ответ 2')),
                ('answer_three_text', models.TextField(blank=True, null=True, verbose_name='Ответ 3')),
                ('answer_three_balls', models.IntegerField(blank=True, null=True, verbose_name='Баллы за ответ 3')),
                ('answer_four_text', models.TextField(blank=True, null=True, verbose_name='Ответ 4')),
                ('answer_four_balls', models.IntegerField(blank=True, null=True, verbose_name='Баллы за ответ 4')),
                ('answer_five_text', models.TextField(blank=True, null=True, verbose_name='Ответ 5')),
                ('answer_five_balls', models.IntegerField(blank=True, null=True, verbose_name='Баллы за ответ 5')),
                ('answer_count', models.IntegerField(verbose_name='Кол-во ответов')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
                'ordering': ['-id'],
            },
        ),
    ]
