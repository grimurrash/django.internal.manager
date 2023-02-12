from django.db import models


class SurveyBotMessage(models.Model):
    chat_id = models.IntegerField('Чат Id')

    class SurveyStatus(models.TextChoices):
        FIRSTNAME = 'FIRSTNAME',
        SURNAME = 'SURNAME',
        LASTNAME = 'LASTNAME',
        SCHOOL = 'SCHOOL',
        PHONE = 'PHONE',
        ARRIVAL_METHOD = 'ARRIVAL_METHOD',
        CAR_BRAND = 'CAR_BRAND',
        CAR_NUMBER = 'CAR_NUMBER'
        END = 'END'

    status = models.CharField('Статус', max_length=20,
                              choices=SurveyStatus.choices,
                              default=SurveyStatus.FIRSTNAME)

    first_name = models.CharField('Имя', max_length=100, default='')
    surname = models.CharField('Фамилия', max_length=100, default='')
    last_name = models.CharField('Отчество', max_length=100, default='')
    school = models.CharField('Образовательная организация', max_length=255, default='')
    phone = models.CharField('Телефон', max_length=100, default='')

    class ArrivalMethod(models.TextChoices):
        BUS = 'BUS',
        CAR = 'CAR'

    arrival_method = models.CharField('Способ прибытия',
                                      max_length=3,
                                      choices=ArrivalMethod.choices,
                                      default=ArrivalMethod.BUS)
    car_brand = models.CharField('Марка машины', max_length=255, default='')
    car_number = models.CharField('Номер машины', max_length=50, default='')

    objects = models.QuerySet.as_manager()

    def __str__(self):
        return f'{self.chat_id}: {self.status}'
