import json
from django.db import models
from django.utils.translation import gettext_lazy as _


class QuerySet(models.QuerySet):
    def to_list(self):
        return_list = []
        for item in self.all():
            return_list.append(item.to_dict())
        return return_list


class ShipType(models.Model):
    name = models.CharField("Название", max_length=255, unique=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    class Meta:
        verbose_name = 'Класс моделей судов'
        verbose_name_plural = 'Классы моделей судов'
        ordering = ['id']

    objects = QuerySet.as_manager()


class ShipModel(models.Model):
    model_name = models.CharField('Название модели', max_length=255)
    model_type = models.ForeignKey(ShipType, verbose_name='Класс модели', null=True, blank=True,
                                   default=None, on_delete=models.SET_NULL)
    model_scale = models.CharField('Маштаб модели', max_length=255)

    class ShopModelStatus(models.IntegerChoices):
        Moderation = 0, _('На модерации')
        Received = 1, _('Принят')
        Not_Nice = 2, _('Не принят')

    status = models.IntegerField(choices=ShopModelStatus.choices, default=ShopModelStatus.Moderation)

    surname = models.CharField('Имя', max_length=100)
    first_name = models.CharField('Фамилия', max_length=100)
    last_name = models.CharField('Отчество', max_length=100)
    date_of_birth = models.DateField('Дата рождения', blank=False, null=False)
    educational_organization = models.CharField('Образовательная организация', max_length=255)
    email = models.CharField('Электронная почта', max_length=100)
    phone_number = models.CharField('Телефон', max_length=20)
    zip_code = models.CharField('Почтовый код', max_length=20)
    city_country = models.CharField('Город/страна', max_length=255)
    actual_address = models.CharField('Фактический адрес', max_length=255)

    description = models.TextField('Описание', default='', blank=True)

    model_passport = models.CharField('Паспорт модели', max_length=255, null=True, default=None)
    model_drawing = models.CharField('Чертёж модели', max_length=255, null=True, default=None)

    main_photo = models.CharField('Основное фото', null=True, blank=False, max_length=255)
    model_photos = models.JSONField('Фотографии модели', default=None, null=True, blank=True)

    def get_status_name(self):
        return self.ShopModelStatus(self.status).label

    def __str__(self):
        return f'#{self.id} {self.model_name} ({self.get_status_name()})'

    class Meta:
        verbose_name = 'Модел судна'
        verbose_name_plural = 'Модели судов'
        ordering = ['-id']

    objects = QuerySet.as_manager()

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'model_name': self.model_name,
            'model_class': str(self.model_type),
            'model_scale': self.model_scale,
            'author': f'{self.surname} {self.first_name} {self.last_name}',
            'main_photo': f'/{self.main_photo}' if self.main_photo else None,
            'model_passport': f'/{self.model_passport}' if self.model_passport else None,
            'model_drawing': f'/{self.model_drawing}' if self.model_drawing else None,
            'city_country': self.city_country,
            'educational_organization': self.educational_organization,
            'description': self.description,
            'photos': list(map(lambda url: f'/{url}', json.loads(self.model_photos)))
        }
