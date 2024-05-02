import gspread
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from museumregistration.utils import MicrosoftGraph
from datetime import datetime

class RegistrationMember(models.Model):
    surname = models.CharField('Имя', max_length=100)
    first_name = models.CharField('Фамилия', max_length=100)
    last_name = models.CharField('Отчество', max_length=100)
    age = models.IntegerField('Возраст', blank=False, null=False)
    parent_fullname = models.CharField('Фамилия', max_length=255)
    phone_number = models.CharField('Телефон', max_length=20)
    reserve_phone_number = models.CharField('Телефон', max_length=20)
    email = models.CharField('Электронная почта', max_length=100)
    actual_address = models.CharField('Фактический адрес', max_length=255)
    school = models.CharField('Школа', max_length=255)
    documents_link = models.CharField('Ссылка на архив с файлами', max_length=255)

    class FamilyStatus(models.IntegerChoices):
        NO_STATUS = 0, _('Без статуса')
        LARGE_FAMILY = 1, _('Многодетная')
        POORLY_SECURED = 2, _('Малообеспеченная')
        NO_GUARDIANSHIP = 3, _('Без попечения')
        INVALID = 4, _('Дети военных по мобилизаци')

    class AgeGroup(models.IntegerChoices):
        FROM_SEVEN_TO_EIGHT = 0, _('От 7 до 8 лет')
        FROM_EIGHT_TO_TEN = 1, _('От 8 до 10 лет')
        FROM_ELEVEN_TO_THIRTEEN = 2, _('От 11 до 13 лет')

    class Direction(models.IntegerChoices):
        TECHNICAL = 0, _('Техническое')
        HISTORY = 1, _('Историческое')
        CIVIL_PATRIOTIC = 2, _('Гражданско - патриотическое')
        MEDIA = 3, _('Медиа')
        MURZILKI = 4, _('Мурзилки')
        ENVIRONMENT = 5, _('Экологическое')
        CHILDREBN_SELF_GOVERNMENT = 6, _('Детское самоуправление')
        WE_ARE_THE_WORLD = 7, _('Мы - это мир')
        CREATIVE = 8, _('Творческое')
        SPORTS = 9, _('Спортивное')

    class Shift(models.IntegerChoices):
        ONE = 0, _('18 - 22 марта')
        TWO = 1, _('8 - 12 апреля')

        @staticmethod
        def get_open_shift():
            now = datetime.now()
            open_shift = 0
            if now >= datetime(2024, 3, 15, 9):
                open_shift = 2
            elif now >= datetime(2024, 2, 27, 13):
                open_shift = 1
            return open_shift

        @staticmethod
        def get_disabled_shift():
            now = datetime.now()
            disabled_shift = 0
            if now >= datetime(2024, 4, 5):
                disabled_shift = 2
            elif now >= datetime(2024, 3, 18, 1):
                disabled_shift = 1
            return disabled_shift

    family_status = models.IntegerField(choices=FamilyStatus.choices, default=FamilyStatus.LARGE_FAMILY)
    direction = models.IntegerField(choices=Direction.choices, default=Direction.TECHNICAL)
    age_group = models.IntegerField(choices=AgeGroup.choices, default=AgeGroup.FROM_EIGHT_TO_TEN)
    shift = models.IntegerField(choices=Shift.choices, default=Shift.ONE)

    def get_family_status(self):
        return self.FamilyStatus(self.family_status).label

    def get_direction(self):
        return self.Direction(self.direction).label

    def get_age_group(self):
        return self.AgeGroup(self.age_group).label

    def get_shift(self):
        return self.Shift(self.shift).label

    def __str__(self):
        return f'{self.surname} {self.first_name} {self.last_name}; {self.school}'

    class Meta:
        verbose_name = 'Заявка на участие "Весна побед"'
        verbose_name_plural = 'Заявки на участие "Весна побед"'
        ordering = ['-id']

    objects = models.QuerySet.as_manager()

    @classmethod
    def registration_limit(cls):
        registration_members = cls.objects.all()
        limit = {}
        for shiftChoice in cls.Shift.choices:
            shift = shiftChoice[0]
            limit.setdefault(shift, {
                cls.Direction.TECHNICAL: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 15,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.MEDIA: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 15,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.HISTORY: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 15,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.MURZILKI: {
                    cls.AgeGroup.FROM_SEVEN_TO_EIGHT: 30,
                },
                cls.Direction.CHILDREBN_SELF_GOVERNMENT: {
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.ENVIRONMENT: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 15,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.CREATIVE: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 15,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.CIVIL_PATRIOTIC: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 15,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.WE_ARE_THE_WORLD: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 15,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.SPORTS: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                }
            })
            for direction in limit[shift]:
                for age in limit[shift][direction]:
                    new_value = limit[shift][direction][age] - registration_members.filter(
                        direction=direction,
                        age_group=age,
                        shift=shift
                    ).count()
                    limit[shift][direction][age] = new_value
        return limit

    def save_to_google_table(self):
        def next_available_row(worksheet):
            str_list = list(filter(None, worksheet.col_values(1)))
            return str(len(str_list) + 1)

        gc = gspread.service_account(settings.GOOGLE_CREDENTIALS_FILE_PATH)
        spreadsheet = gc.open_by_key(settings.GOOGLE_MUSEUMREGISTRATION_SPREADSHEET_ID)
        sheet = spreadsheet.worksheet('Весна 2024')
        next_row = next_available_row(sheet)
        sheet.update(f'A{next_row}', [
            [str(self.surname), str(self.first_name), str(self.last_name),
             str(self.age),
             str(self.actual_address), str(self.school),
             str(self.parent_fullname), str(self.phone_number), str(self.reserve_phone_number), str(self.email),
             str(self.get_family_status()), str(self.get_direction()),
             str(self.get_age_group()), str(self.get_shift()), str(self.documents_link)]])

    def send_email_notification(self):
        from_addr = "leto_pobed@cpvs.moscow"
        support_addr = ''
        content = f"""
            <p>Спасибо!,</p>
<p>Документы приняты к рассмотрению.</p>
<p>Модерация документов проводится в течении 3-5 рабочих дней.</p>
<p>По итогам вы получите уведомление на указанную электронную почту.".</p>
        """

        send_result = MicrosoftGraph.send_mail(
            from_address=from_addr,
            to_address=str(self.email),
            message=content,
            subject='Регистрация на "Городской детский клуб "Весна Побед"'
        )
        if not send_result and support_addr:
            MicrosoftGraph.send_mail(
                from_address=from_addr,
                to_address=support_addr,
                message=f"""
                ФИО ребенка: {self.surname} {self.first_name} {self.last_name}
                ФИО родителя: {self.parent_fullname}
                Электронная почта: {self.email}
                Телефон: {self.phone_number}
                """,
                subject='Не получилось отправить письмо о подтверждении регистрации'
            )