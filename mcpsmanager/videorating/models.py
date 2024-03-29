from django.db import models


class Participant(models.Model):
    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участник'
        ordering = ['-id']

    type = models.CharField('Тип учатсника', max_length=255)

    school = models.CharField('Наименование школы', max_length=255, null=True, blank=True, default=None)
    team_name = models.CharField('Наименование отряда', max_length=255, null=True, blank=True, default=None)
    video_url = models.CharField('Видео ссылка', max_length=2000, null=True, blank=True, default=None)
    leader_fio = models.CharField('Руководитель ФИО', max_length=255, null=True, blank=True, default=None)
    reference_url = models.CharField('Справка ссылка', max_length=2000, null=True, blank=True, default=None)

    objects = models.QuerySet.as_manager()

    def __str__(self):
        return self.school

    def to_dict(self, participant_evaluations, there_rating):
        points = participant_evaluations.aggregate(models.Avg('points')).get('points__avg')
        comments = []
        for participant_evaluation in participant_evaluations:
            if participant_evaluation.comment is not None:
                comments.append(f"{participant_evaluation.appraiser}: {participant_evaluation.comment}")

        return {
            'id': self.id,
            'type': self.type,
            'school': self.school,
            'name_team': self.team_name,
            'video_url': self.video_url,
            'leader_fio': self.leader_fio,
            'reference_url': self.reference_url,
            'evaluation': points,
            'there_rating': there_rating,
            'comments': comments
        }


class Evaluation(models.Model):
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценка'
        ordering = ['-id']

    appraiser = models.CharField('Оценщик', max_length=255)
    points = models.FloatField('Баллов')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, verbose_name='Участник')
    comment = models.TextField('Комментарий',null=True, blank=True, default=None)

    def __str__(self):
        return f'{self.appraiser} - {self.points}'

    objects = models.QuerySet.as_manager()