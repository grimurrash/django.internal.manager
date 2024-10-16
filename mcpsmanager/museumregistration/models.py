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
    age = models.IntegerField('Возраст', blank=False, null=False, default=0)
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
        FROM_SEVEN_TO_EIGHT = 0, _('8 лет')
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
        ONE = 0, _('27 - 31 мая')
        TWO = 1, _('3 - 7 июня')
        THREE = 2, _('10 - 14 июня')
        FOUR = 3, _('17 - 21 июня')
        FIVE = 4, _('24 - 28 июня')
        SIX = 5, _('1 - 5 июля')
        SEVEN = 6, _('8 - 12 июля')
        EIGHT = 7, _('15 - 19 июля')
        NINE = 8, _('22 - 26 июля')
        TEN = 9, _('29 июля - 2 августа')
        ELEVEN = 10, _('5 - 9 августа')
        TWELVE = 11, _('12 - 16 августа')
        THIRTEEN = 12, _('19 - 23 августа')

        @staticmethod
        def get_open_shift():
            now = datetime.now()
            open_shift = 0
            if now >= datetime(2024, 7, 8, 10):
                open_shift = 13
            elif now >= datetime(2024, 6, 17, 10):
                open_shift = 8
            elif now >= datetime(2024, 6, 3, 10):
                open_shift = 4    
            elif now >= datetime(2024, 5, 17, 10):
                open_shift = 2
            return open_shift

        @staticmethod
        def get_disabled_shift():
            now = datetime.now()
            disabled_shift = 0
            # За день до старта смены, она становится недоступкой к регистрации
            if now >= datetime(2024, 8, 18, 12):
                disabled_shift = 13
            elif now >= datetime(2024, 8, 11, 12):
                disabled_shift = 12
            elif now >= datetime(2024, 8, 4, 12):
                disabled_shift = 11
            elif now >= datetime(2024, 7, 28, 12):
                disabled_shift = 10
            elif now >= datetime(2024, 7, 21, 12):
                disabled_shift = 9
            elif now >= datetime(2024, 7, 14, 12):
                disabled_shift = 8
            elif now >= datetime(2024, 7, 7, 12):
                disabled_shift = 7
            elif now >= datetime(2024, 6, 30, 12):
                disabled_shift = 6
            elif now >= datetime(2024, 6, 23, 12):
                disabled_shift = 5
            elif now >= datetime(2024, 6, 16, 12):
                disabled_shift = 4
            elif now >= datetime(2024, 6, 9, 12):
                disabled_shift = 3
            elif now >= datetime(2024, 6, 2, 12):
                disabled_shift = 2
            elif now >= datetime(2024, 5, 26, 12):
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
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.MEDIA: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
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
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 15,
                },
                cls.Direction.CREATIVE: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.CIVIL_PATRIOTIC: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
                },
                cls.Direction.WE_ARE_THE_WORLD: {
                    cls.AgeGroup.FROM_EIGHT_TO_TEN: 20,
                    cls.AgeGroup.FROM_ELEVEN_TO_THIRTEEN: 20,
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
        sheet = spreadsheet.worksheet('Лето 2024')
        next_row = next_available_row(sheet)
        sheet.update(f'A{next_row}', [
            [str(self.surname), str(self.first_name), str(self.last_name),
             str(self.age),
             str(self.actual_address), str(self.school),
             str(self.parent_fullname), str(self.phone_number), str(self.reserve_phone_number), str(self.email),
             str(self.get_family_status()), str(self.get_direction()),
             str(self.get_age_group()), str(self.get_shift()), str(self.documents_link)]])

    # def send_email_notification(self):
    #     shift_start_dates = {
    #         0: "30 мая",
    #         1: "6 июня",
    #         2: "13 июня",
    #         3: "20 июня",
    #         4: "27 июня",
    #         5: "4 июля",
    #         6: "11 июля",
    #         7: "18 июля",
    #         8: "25 июля",
    #         9: "1 августа",
    #         10: "8 августа",
    #         11: "15 августа",
    #         12: "22 августа",
    #     }
    #
    #     start_date = shift_start_dates.get(self.shift)
    #     from_addr = "leto_pobed@cpvs.moscow"
    #     support_addr = ''
    #     content = f"""
    #         <p>Вы зарегистрировали ребенка для участия в совместном проекте Департамента образования
    #         и науки города Москвы и Музея Победы "Городской детский клуб "Лето Побед".</p>
    #         <br>
    #         <p>В течение 3-4 дней проводится ручная модерация и проверка предоставленных вами документов. Ожидайте на указанную вами почту письмо либо с приглашением и "Памяткой для родителей", либо отказ (если ваш льготный статус не подтвержден или документы некорректно прикреплены). Обычно письмо приходит в четверг или пятницу перед началом смены.</p>
    #     """
    #
    #     send_result = MicrosoftGraph.send_mail(
    #         from_address=from_addr,
    #         to_address=str(self.email),
    #         message=content,
    #         subject='Регистрация на "Городской детский клуб "Лето Побед"'
    #     )
    #     if not send_result and support_addr:
    #         MicrosoftGraph.send_mail(
    #             from_address=from_addr,
    #             to_address=support_addr,
    #             message=f"""
    #             ФИО ребенка: {self.surname} {self.first_name} {self.last_name}
    #             ФИО родителя: {self.parent_fullname}
    #             Электронная почта: {self.email}
    #             Телефон: {self.phone_number}
    #             """,
    #             subject='Не получилось отправить письмо о подтверждении регистрации'
    #         )
