# Generated by Django 3.2.8 on 2021-11-07 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('microsoft_id', models.CharField(max_length=255, verbose_name='Id в Microsoft')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование группы')),
            ],
            options={
                'verbose_name': 'Группа',
                'verbose_name_plural': 'Группы',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TeamsEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование мероприятия')),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятия',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('microsoft_id', models.CharField(max_length=255, verbose_name='ID в microsoft')),
                ('email', models.CharField(max_length=255, verbose_name='email')),
                ('password', models.CharField(max_length=255, verbose_name='password')),
                ('personal_email', models.CharField(max_length=255, verbose_name='Личная почта')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamsevent.group')),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='group',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamsevent.teamsevent'),
        ),
    ]
