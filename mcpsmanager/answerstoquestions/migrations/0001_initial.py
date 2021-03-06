# Generated by Django 4.0.4 on 2022-05-17 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255, verbose_name='Вопрос')),
                ('yes_answer', models.IntegerField(default=0, verbose_name='Ответов ДА')),
                ('no_answer', models.IntegerField(default=0, verbose_name='Ответов НЕТ')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
                'ordering': ['-id'],
            },
        ),
    ]
