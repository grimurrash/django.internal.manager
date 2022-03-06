from django.db import models


class TimelineEventQuerySet(models.QuerySet):
    def to_list(self):
        return_list = []
        for event in self.all():
            return_list.append(event.to_dict())
        return return_list


class TimelineEvent(models.Model):
    event_name = models.CharField('Наименование события', max_length=255, blank=False)
    description = models.TextField('Основной текст')
    source = models.CharField('Источник', max_length=255, blank=True)
    event_date = models.DateField('Дата события', blank=False, null=False)
    images = models.TextField('Ссылки на изображения', blank=True, null=True)
    video = models.CharField('Ссылка на видео', max_length=255, blank=True, null=True)
    tags = models.CharField('Теги (через запятую)', max_length=255, blank=True, null=True)

    objects = TimelineEventQuerySet.as_manager()

    def __str__(self):
        return f'Событие {self.event_name} ({self.event_date})'

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['-id']

    def to_dict(self):
        images = []
        tags = []
        preview = ''
        if self.images:
            images = str(self.images).split('\r\n')
            preview = images[0]
        if self.tags:
            tags = str(self.tags).split(',')
        return {
            'id': self.id,
            'name': self.event_name,
            'source': self.source,
            'description': self.description,
            'date': self.event_date,
            'preview': preview,
            'images': images,
            'video': self.video,
            'tags': tags,
        }
