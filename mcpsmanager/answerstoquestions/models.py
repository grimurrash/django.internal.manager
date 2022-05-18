from django.db import models


class Question(models.Model):
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-id']

    question = models.TextField('Вопрос')
    yes_answer = models.IntegerField('Ответов ДА', default=0)
    no_answer = models.IntegerField('Ответов НЕТ', default=0)
    yes_answer_name = models.CharField('Ответ ДА', max_length=255, blank=True)
    no_answer_name = models.CharField('Ответ НЕТ', max_length=255, blank=True)

    objects = models.QuerySet.as_manager()

    def get_form_url(self):
        return f'http://questions-event.cpvs.moscow/{self.id}'

    def get_chart_url(self):
        return f'http://questions-event.cpvs.moscow/chart/{self.id}'

    def add_yes_answer(self):
        self.yes_answer = self.yes_answer + 1
        self.save()

    def add_no_answer(self):
        self.no_answer = self.no_answer + 1
        self.save()