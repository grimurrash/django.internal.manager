import gspread
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from museumregistration.utils import MicrosoftGraph

from datetime import datetime
import pytz

class RegistrationMember(models.Model):
    surname = models.CharField('Имя', max_length=100)
    first_name = models.CharField('Фамилия', max_length=100)
    last_name = models.CharField('Отчество', max_length=100)
    date_of_birth = models.DateField('Дата рождения', blank=False, null=False)
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
        INVALID = 4, _('Дети военных  по мобилизаци')

    class AgeGroup(models.IntegerChoices):
        FROM_EIGHT_TO_TEN = 0, _('От 8 до 10 лет')
        FROM_ELEVEN_TO_THIRTEEN = 1, _('От 11 до 13 лет')

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

    class Shift(models.IntegerChoices):
        ONE = 0, _('29 мая - 2 июня')
        TWO = 1, _('5 - 9 июня')
        THREE = 2, _('12 - 16 июня')
        FOUR = 3, _('19 - 23 июня')
        FIVE = 4, _('26 - 30 июня')
        SIX = 5, _('3 - 7 июля')
        SEVEN = 6, _('10 - 14 июля')
        EIGHT = 7, _('17 - 21 июля')
        NINE = 8, _('24 - 28 июля')
        TEN = 9, _('31 июля - 4 августа')
        ELEVEN = 10, _('07 - 11 августа')
        TWELVE = 11, _('14 - 18 августа')
        THIRTEEN = 12, _('21 - 25 августа')

        @staticmethod
        def get_open_shift():
            now = datetime.now()
            open_shift = 2
            if now >= datetime(2023, 6, 26, 10):
                open_shift = 13
            elif now >= datetime(2023, 6, 19, 10):
                open_shift = 11
            elif now >= datetime(2023, 6, 13, 10):
                open_shift = 10
            elif now >= datetime(2023, 6, 5, 10):
                open_shift = 8
            elif now >= datetime(2023, 5, 29, 10):
                open_shift = 6
            elif now >= datetime(2023, 5, 15, 10):
                open_shift = 4
            return open_shift

        @staticmethod
        def get_disabled_shift():
            now = datetime.now()
            disabled_shift = 0
            if now >= datetime(2023, 8, 21):
                disabled_shift = 13
            elif now >= datetime(2023, 8, 14):
                disabled_shift = 12
            elif now >= datetime(2023, 8, 7):
                disabled_shift = 11
            elif now >= datetime(2023, 7, 31):
                disabled_shift = 10
            elif now >= datetime(2023, 7, 24):
                disabled_shift = 9
            elif now >= datetime(2023, 7, 17):
                disabled_shift = 8
            elif now >= datetime(2023, 7, 10):
                disabled_shift = 7
            elif now >= datetime(2023, 7, 3):
                disabled_shift = 6
            elif now >= datetime(2023, 6, 26):
                disabled_shift = 5
            elif now >= datetime(2023, 6, 19):
                disabled_shift = 4
            elif now >= datetime(2023, 6, 12):
                disabled_shift = 3
            elif now >= datetime(2023, 6, 5):
                disabled_shift = 2
            elif now >= datetime(2023, 5, 29):
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

    def get_date_of_birth(self):
        return

    def __str__(self):
        return f'{self.surname} {self.first_name} {self.last_name}; {self.school}'

    class Meta:
        verbose_name = 'Заявка на участие'
        verbose_name_plural = 'Заявки на участие'
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
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 25,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 25,
                },
                cls.Direction.MEDIA: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.HISTORY: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.MURZILKI: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 30,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 0,
                },
                cls.Direction.CHILDREBN_SELF_GOVERNMENT: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 0,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.ENVIRONMENT: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.CREATIVE: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.CIVIL_PATRIOTIC: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 25,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 25,
                },
                cls.Direction.WE_ARE_THE_WORLD: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
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

    def save_to_google_table(self, spreadsheet_id):
        def next_available_row(worksheet):
            str_list = list(filter(None, worksheet.col_values(1)))
            return str(len(str_list) + 1)

        gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
        spreadsheet = gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet('Участники 2023')
        next_row = next_available_row(sheet)
        sheet.update(f'A{next_row}', [
            [str(self.surname), str(self.first_name), str(self.last_name),
             str(self.date_of_birth)[0:10],
             str(self.actual_address), str(self.school),
             str(self.parent_fullname), str(self.phone_number), str(self.reserve_phone_number), str(self.email),
             str(self.get_family_status()), str(self.get_direction()),
             str(self.get_age_group()), str(self.get_shift()), str(self.documents_link)]])

    def send_email_notification(self):
        shift_start_dates = {
            0: "30 мая",
            1: "6 июня",
            2: "13 июня",
            3: "20 июня",
            4: "27 июня",
            5: "4 июля",
            6: "11 июля",
            7: "18 июля",
            8: "25 июля",
            9: "1 августа",
            10: "8 августа",
            11: "15 августа",
            12: "22 августа",
        }

        start_date = shift_start_dates.get(self.shift)
        from_addr = "leto_pobed@cpvs.moscow"
        support_addr = ''
        content = f"""
            <p>Вы зарегистрировали ребенка для участия в совместном проекте Департамента образования 
            и науки города Москвы и Музея Победы "Городской детский клуб "Лето Побед".</p>
            <br>
            <p>В течение 3-4 дней проводится ручная модерация и проверка предоставленных вами документов. Ожидайте на указанную вами почту письмо либо с приглашением и "Памяткой для родителей", либо отказ (если ваш льготный статус не подтвержден или документы некорректно прикреплены). Обычно письмо приходит в четверг или пятницу перед началом смены.</p>
        """

        send_result = MicrosoftGraph.send_mail(
            from_address=from_addr,
            to_address=str(self.email),
            message=content,
            subject='Регистрация на "Городской детский клуб "Лето Побед"'
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
