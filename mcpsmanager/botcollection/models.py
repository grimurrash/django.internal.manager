from django.db import models


class SurveyBotMessage(models.Model):
    chat_id = models.IntegerField('Чат Id')

    class SurveyStatus(models.TextChoices):
        FIRSTNAME = 'FIRSTNAME',
        SURNAME = 'SURNAME',
        LASTNAME = 'LASTNAME',
        SCHOOL = 'SCHOOL',
        EMAIL = 'EMAIL',
        ARRIVAL_METHOD = 'ARRIVAL_METHOD',
        END = 'END'

    status = models.CharField('Статус', max_length=20,
                              choices=SurveyStatus.choices,
                              default=SurveyStatus.FIRSTNAME)

    first_name = models.CharField('Имя', max_length=100, default='')
    surname = models.CharField('Фамилия', max_length=100, default='')
    last_name = models.CharField('Отчество', max_length=100, default='')
    school = models.CharField('Школа', max_length=255, default='')
    email = models.CharField('Почта', max_length=255, default='')

    class ArrivalMethod(models.TextChoices):
        BUS = 'BUS',
        CAR = 'CAR'

    arrival_method = models.CharField('Способ прибытия',
                                      max_length=3,
                                      choices=ArrivalMethod.choices,
                                      default=ArrivalMethod.BUS)

    objects = models.QuerySet.as_manager()

    def __str__(self):
        return f'{self.chat_id}: {self.status}'
