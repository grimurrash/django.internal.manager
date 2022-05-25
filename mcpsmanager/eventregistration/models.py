import gspread
from django.db import models
from django.conf import settings
from gspread import Worksheet
from museumregistration.utils import MicrosoftGraph


class QuerySet(models.QuerySet):
    def to_list(self):
        return_list = []
        for item in self.all():
            return_list.append(item.to_dict())
        return return_list


class Event(models.Model):
    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятие'
        ordering = ['-id']

    name = models.CharField('Наименование', max_length=255)
    slug = models.CharField('Анг наименование (используется для ссылки)', max_length=255, unique=True)

    limit_for_one_user = models.PositiveIntegerField('Лимит регистраций для одного пользователя', default=100)

    is_save_google_table = models.BooleanField('Сохранять в гугл таблице', default=False)
    google_spreadsheet_id = models.CharField('Гугл таблица', max_length=255, default=None, null=True, blank=True)

    is_send_registration_mail_notification = models.BooleanField('Отправлять письмо о регистрации', default=False)
    from_email_address = models.CharField('Почта для рассылок', max_length=255, default=None, null=True, blank=True)
    registration_mail_subject = models.CharField('Тема письма о регистрации', max_length=255, default=None, null=True,
                                                 blank=True)
    registration_mail_text = models.TextField('Текст письма о регистрации', default=None, null=True,
                                              blank=True)
    reminder_mail_text = models.TextField('Текст письма с напоминанием', default=None, null=True,
                                          blank=True)

    support_email_address = models.CharField('Почта поддержки', max_length=255)

    objects = QuerySet.as_manager()

    class SaveDataToGoogleTableError(Exception):
        message = ''

        def __init__(self, message=''):
            message = message

        def __str__(self):
            return f"Ошибка сохранения данных в гугл таблицу | {self.message}"

    def __str__(self):
        return self.name

    def get_full_info(self):
        documents = Documents.objects.filter(event=self).order_by('id')
        shifts = Shift.objects.filter(event=self).order_by('id')
        age_groups = AgeGroup.objects.filter(event=self).order_by('id')
        directions = Direction.objects.filter(event=self).order_by('id')
        limits = EventLimit.objects.filter(event=self)
        return {
            'id': int(self.id),
            'name': str(self.name),
            'slug': str(self.slug),
            'shifts': shifts.to_list(),
            'age_groups': age_groups.to_list(),
            'directions': directions.to_list(),
            'documents': documents.to_list(),
            'limits': limits.to_list(),
            'support': self.support_email_address
        }

    def save_google_table(self, data: list, table_name: str = 'Участники'):
        try:
            if not self.is_save_google_table or not self.google_spreadsheet_id:
                return

            def next_available_row(l_worksheet: Worksheet):
                str_list = list(filter(None, l_worksheet.col_values(1)))
                return str(len(str_list) + 1)

            gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
            spreadsheet = gc.open_by_key(str(self.google_spreadsheet_id))
            worksheets = list(spreadsheet.worksheets())
            is_exist_sheet = False
            print(worksheets)
            for worksheet in worksheets:
                if worksheet.title == table_name:
                    is_exist_sheet = True
                    break
            print(is_exist_sheet)
            if is_exist_sheet:
                sheet = spreadsheet.worksheet(table_name)
            else:
                sheet = spreadsheet.add_worksheet(table_name, 100, 500)
            print(sheet)
            next_row = next_available_row(sheet)
            print(next_row)
            print(data)
            sheet.update(f'A{next_row}', [data])
        except Exception as exception:
            raise self.SaveDataToGoogleTableError(str(exception))

    def send_support(self, subject: str, message: str):
        MicrosoftGraph.send_mail(
            from_address=str(self.from_email_address),
            to_address=str(self.support_email_address),
            message=message,
            subject=subject
        )


class Documents(models.Model):
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-id']

    name = models.CharField('Наименование', max_length=255)
    btn_name = models.CharField('Текст в кнопке', max_length=255, default='')
    is_have_checkbox = models.BooleanField('Нужен чекбокс?', default=True)
    checkbox_text = models.CharField('Текст чекбокса', max_length=255, default='')
    file = models.FileField(upload_to='uploads/documents/%Y-%m-%d/')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    is_upload = models.BooleanField('Нужно ли пользователю загружать документ?', default=False)
    show_conditions = models.CharField('Специальные условия вывода', max_length=50, default=None, null=True, blank=True)

    objects = QuerySet.as_manager()

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.file.url,
            'btn_name': self.btn_name,
            'is_have_checkbox': self.is_have_checkbox,
            'checkbox_text': self.checkbox_text,
            'is_upload': self.is_upload,
            'show_conditions': self.show_conditions,
            'event_id': self.event_id,
        }


class Shift(models.Model):
    class Meta:
        verbose_name = 'Смена'
        verbose_name_plural = 'Смены'
        ordering = ['-id']

    name = models.CharField('Наименование', max_length=255)
    shift_start_date = models.DateTimeField('Дата начала', blank=True, null=True)
    shift_end_date = models.DateTimeField('Дата завершения', blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    objects = QuerySet.as_manager()

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'shift_start_date': self.shift_start_date,
            'shift_end_date': self.shift_end_date,
            'event_id': self.event_id,
        }


class AgeGroup(models.Model):
    class Meta:
        verbose_name = 'Возрастная группа'
        verbose_name_plural = 'Возрастная группы'
        ordering = ['-id']

    name = models.CharField('Наименование', max_length=255)
    min = models.PositiveIntegerField('Минимальный возраст', default=None, blank=True, null=True)
    max = models.PositiveIntegerField('Максимальный возраст', default=None, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    objects = QuerySet.as_manager()

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'min': self.min,
            'max': self.max,
            'event_id': self.event_id,
        }


class Direction(models.Model):
    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'
        ordering = ['-id']

    name = models.CharField('Наименование', max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    objects = QuerySet.as_manager()

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'event_id': self.event_id,
        }


class EventLimit(models.Model):
    class Meta:
        verbose_name = 'Ограничения кол-ва'
        verbose_name_plural = 'Ограничение кол-ва'
        ordering = ['-id']

    limit = models.PositiveIntegerField('Максимальное кол-во', default=10000)
    free_seats = models.PositiveIntegerField('Осталось мест', default=10000)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name='Смена', null=True, blank=True,
                              default=None)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, verbose_name='Направление', null=True,
                                  blank=True, default=None)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE, verbose_name='Возрастная группа', null=True,
                                  blank=True, default=None)

    objects = QuerySet.as_manager()

    def __str__(self):
        return self.get_name()

    def get_name(self):
        name = self.event.name
        if self.shift:
            name += f" {self.shift.name}"
        if self.direction:
            name += f" {self.direction.name}"
        if self.age_group:
            name += f" {self.age_group.name}"
        return name

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'shift_id': self.shift_id,
            'direction_id': self.direction_id,
            'age_group_id': self.age_group_id,
            'limit': self.limit,
            'free_seats': self.free_seats,
        }


class Participant(models.Model):
    class Meta:
        verbose_name = 'Регистрация участников'
        verbose_name_plural = 'Регистрация участников'
        ordering = ['-id']

    surname = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Отчество', max_length=100)
    date_of_birth = models.DateField('Дата рождения', blank=False, null=False)
    email = models.CharField('Электронная почта', max_length=100)

    additionally_data = models.JSONField('Дополнительная информация', null=True, blank=True, default=None)

    is_send_registration_mail = models.BooleanField('Было ли отправлено письмо о регистрации', default=False)
    is_send_reminder_mail = models.BooleanField('Было ли отправлено письмо с напоминанием', default=False)

    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name='Смена', null=True, blank=True,
                              default=None)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE, verbose_name='Смена', null=True, blank=True,
                                  default=None)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, verbose_name='Смена', null=True, blank=True,
                                  default=None)
    files_dir = models.CharField('Папка с файлами', max_length=255, default=None, blank=True, null=True)

    objects = QuerySet.as_manager()

    def __str__(self):
        return f'{self.surname} {self.first_name} {self.last_name}; {self.date_of_birth}'
