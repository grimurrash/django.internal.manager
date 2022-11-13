import json

import gspread
from django.conf import settings
from django.db import models
from gspread import Worksheet


class QuerySet(models.QuerySet):
    def to_list(self):
        return_list = []
        for item in self.all():
            return_list.append(item.to_dict())
        return return_list


class Survey(models.Model):
    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering = ['-id']

    name = models.CharField('Наименование', max_length=255)
    url = models.CharField('Ссылка', max_length=255)

    google_spreadsheet_id = models.CharField('Гугл таблица', max_length=255, default=None, null=True, blank=True)

    background_image = models.FileField(
        'Фоновое изображение',
        upload_to='uploads/background/%Y-%m-%d/',
        default=None,
        blank=True,
        null=True
    )

    objects = QuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_info(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'backgroundImage': (settings.APP_URL + self.background_image.url) if self.background_image else '',
        }


class SurveyAnswer(models.Model):
    class Meta:
        verbose_name = 'Ответ на опрос'
        verbose_name_plural = 'Ответы на опросы'
        ordering = ['-id']

    data = models.JSONField('Данные', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name='Опрос', default=None)

    objects = QuerySet.as_manager()

    def __str__(self):
        return f'{self.survey.name} {self.id}'

    @classmethod
    def create(cls, survey: Survey, data: dict):
        answer = cls(
            survey=survey,
            data=json.dumps(data),
        )
        answer.save()

        answer.save_google_table()

    def save_google_table(self):
        try:
            if not self.survey or not self.survey.google_spreadsheet_id:
                return False

            table_id = self.survey.google_spreadsheet_id
            table_name = self.survey.name

            save_data = [self.id]
            data = json.loads(str(self.data))
            for key, value in data.items():
                save_data.append(str(value))

            def next_available_row(l_worksheet: Worksheet):
                str_list = list(filter(None, l_worksheet.col_values(1)))
                return len(str_list) + 1

            gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
            spreadsheet = gc.open_by_key(table_id)
            worksheets = list(spreadsheet.worksheets())
            is_exist_sheet = False
            for worksheet in worksheets:
                if worksheet.title == table_name:
                    is_exist_sheet = True
                    break
            if is_exist_sheet:
                sheet = spreadsheet.worksheet(table_name)
            else:
                sheet = spreadsheet.add_worksheet(table_name, 1, len(save_data) + 1)

            next_row = next_available_row(sheet)
            sheet.add_rows(1)
            sheet.update(f'A{next_row}', [save_data])
            return True
        except Exception:
            return False
