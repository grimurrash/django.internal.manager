from django.db import models
import gspread
import random
from django.conf import settings
from django.db.models import Q
from enum import Enum


class Questions(models.Model):
    questing_id = models.IntegerField('Номер вопроса')
    block_name = models.CharField('Блок', max_length=100)
    questing_text = models.TextField('Вопрос')
    answer_one_text = models.TextField('Ответ 1', null=True, blank=True)
    answer_one_balls = models.IntegerField('Баллы за ответ 1', null=True, blank=True)

    answer_two_text = models.TextField('Ответ 2', null=True, blank=True)
    answer_two_balls = models.IntegerField('Баллы за ответ 2', null=True, blank=True)

    answer_three_text = models.TextField('Ответ 3', null=True, blank=True)
    answer_three_balls = models.IntegerField('Баллы за ответ 3', null=True, blank=True)

    answer_four_text = models.TextField('Ответ 4', null=True, blank=True)
    answer_four_balls = models.IntegerField('Баллы за ответ 4', null=True, blank=True)

    answer_five_text = models.TextField('Ответ 5', null=True, blank=True)
    answer_five_balls = models.IntegerField('Баллы за ответ 5', null=True, blank=True)

    answer_count = models.IntegerField('Кол-во ответов')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-id']

    def __str__(self):
        return f'{self.block_name} #{self.questing_id}: {self.questing_text}'

    objects = models.QuerySet.as_manager()

    @classmethod
    def refresh(cls):
        gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
        spreadsheet = gc.open_by_key(settings.ADVISORS_QUESTIONS_SPREADSHEET_ID)
        cls.objects.all().delete()
        worksheets = list(spreadsheet.worksheets())
        for worksheet in worksheets:
            values = list(worksheet.get_all_values())
            for row in values:
                if row[0] == '№':
                    continue

                new_q = cls(
                    questing_id=row[0],
                    block_name=worksheet.title,
                    questing_text=row[2],
                    answer_one_text=row[3] if row[3] != '' else '',
                    answer_one_balls=row[4] if row[4] != '' else 0,
                    answer_two_text=row[5] if row[5] != '' else '',
                    answer_two_balls=row[6] if row[6] != '' else 0,
                    answer_three_text=row[7] if row[7] != '' else '',
                    answer_three_balls=row[8] if row[8] != '' else 0,
                    answer_four_text=row[9] if row[9] != '' else '',
                    answer_four_balls=row[10] if row[10] != '' else 0,
                    answer_five_text=row[11] if row[11] != '' else '',
                    answer_five_balls=row[12] if row[12] != '' else 0,
                    answer_count=row[13]
                )
                new_q.save()

    @classmethod
    def get_questions_list(cls) -> list:
        all_questions = cls.objects.all()

        list_ids = random.sample(range(1, len(all_questions.filter(block_name='Правовые'))), 8)
        list_one = list(all_questions.filter(Q(block_name='Правовые') & Q(questing_id__in=list_ids)))

        list_two_count = len(all_questions.filter(block_name='Психолого-педагогические'))
        if list_two_count > 8:
            list_ids = random.sample(range(1, list_two_count), 8)
            list_two = list(all_questions.filter(Q(block_name='Психолого-педагогические') & Q(questing_id__in=list_ids)))
        else:
            list_two = list(all_questions.filter(block_name='Психолого-педагогические'))

        list_ids = random.sample(range(1, len(all_questions.filter(block_name='Управленческие'))), 8)
        list_three = list(all_questions.filter(Q(block_name='Управленческие') & Q(questing_id__in=list_ids)))

        list_ids = random.sample(range(1, len(all_questions.filter(block_name='Ценностно-содержательные'))), 8)
        list_four = list(all_questions.filter(Q(block_name='Ценностно-содержательные') & Q(questing_id__in=list_ids)))

        question_list = list_one + list_two + list_three + list_four
        random.shuffle(question_list)
        return question_list


class InterviewStep(Enum):
    start = 'start'  # /start
    start_1 = 'start_1'  # С положением ознакомлен
    start_2 = 'start_2'  # Даю согласие на обработку и использование персональных данных
    start_3 = 'start_3'  # Правила заполнения
    start_4 = 'start_4'  # Все понятно
    start_end = 'start_end'  # СТАРТ

    surname = 'surname'
    name = 'firstname'
    patronymic = 'patronymic'
    date_of_birth = 'date_of_birth'
    gender = 'gender'
    photo = 'photo'
    phone_number = 'phone_number'
    email = 'email'
    social_networks = 'social_networks'
    education = 'education'
    place_education = 'place_education'
    place_education_2 = 'place_education_2'
    napr_education = 'napr_education'
    place_education_stop = 'place_education_stop'
    doc_education = 'doc_education'
    add_education = 'add_education'
    work_experience = 'work_experience'
    job_title = 'job_title'
    add_work = 'add_work'
    prof_skills = 'prof_skills'
    pers_qualities = 'pers_qualities'
    achievements = 'achievements'
    exp_children = 'exp_children'
    ed_oo_work = 'ed_oo_work'
    adm_okr = 'adm_okr'
    add_adm_okr = 'add_adm_okr'

    start_test = 'start_test'
    test = 'test'
    finish = 'finish'


class Interview(models.Model):
    chat_id = models.CharField('Chat id', max_length=100)
    step = models.CharField('Этап опроса', max_length=100, default=InterviewStep.start.value)
    interview_answers = models.JSONField('Ответы опроса', default=dict)
    google_table_row = models.IntegerField('Строка в гугл таблице', null=True, blank=True, default=None)
    test_finish_time = models.DateTimeField('Время окончания теста', null=True, blank=True, default=None)
    questing_text = models.JSONField('Вопросы', null=True)
    questing_step = models.IntegerField('Актуальный вопрос', default=-1)
    questing_balls = models.IntegerField('Кол-во балов', default=0)

    objects = models.QuerySet.as_manager()

    class Meta:
        verbose_name = 'Тестирование пользователя'
        verbose_name_plural = 'Тестирование пользователя'
        ordering = ['-id']

    def __str__(self):
        return f'#{self.chat_id}; step - {self.step}'

    def update_step(self, step: InterviewStep):
        self.step = step.value
        self.save()

    def save_interview_answers_to_table(self):
        def next_available_row(worksheet):
            str_list = list(filter(None, worksheet.col_values(1)))
            return str(len(str_list) + 1)

        gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
        spreadsheet = gc.open_by_key(settings.ADVISORS_RESULT_SPREADSHEET_ID)
        sheet = spreadsheet.worksheet('Результаты опроса')
        next_row = next_available_row(sheet)
        interview_answers = dict(self.interview_answers)

        education_list = []
        for value in dict(interview_answers['education_list']).values():
            education_list.append(f'{value["place_education"]}, {value["napr_education"]}, '
                                  f'{value["place_education_stop"]}, '
                                  f'https://manager.cpvs.moscow/{value["doc_education"]};')

        work_list = []
        for value in dict(interview_answers['work_list']).values():
            work_list.append(f'{value["work_experience"]}, {value["job_title"]};')

        sheet.update(f'A{next_row}', [
            [
                interview_answers['surname'],
                interview_answers['name'],
                interview_answers['patronymic'],
                interview_answers['date_of_birth'],
                interview_answers['gender'],
                'https://manager.cpvs.moscow/' + interview_answers['photo'],
                interview_answers['phone_number'],
                interview_answers['email'],
                interview_answers['social_networks'],
                interview_answers['education_level'],
                interview_answers['place_education'],
                '\n'.join(education_list),
                '\n'.join(work_list),
                interview_answers['prof_skills'],
                interview_answers['pers_qualities'],
                interview_answers['achievements'],
                interview_answers['exp_children'],
                interview_answers['ed_oo_work'],
                ', '.join(list(interview_answers['adm_okr_list'])),
            ]
        ])
        self.google_table_row = next_row

    def save_test_result_to_table(self):
        gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
        spreadsheet = gc.open_by_key(settings.ADVISORS_RESULT_SPREADSHEET_ID)
        sheet = spreadsheet.worksheet('Результаты опроса')
        sheet.update(f'T{self.google_table_row}', str(self.questing_balls))
