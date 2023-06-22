import json
import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from botadvisors.models import *
from telegram import *
from munch import DefaultMunch
from datetime import datetime, timedelta
from pathlib import Path


def interview_step(user_interview: Interview, bot: Bot, update: Update):
    if update.message.text and update.message.text == '/refresh':
        user_interview.step = InterviewStep.start_test.value
        user_interview.save()
        keyboard_markup = [[
            KeyboardButton(text='Начать тестирование'),
        ]]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Тестирование обнулено!',
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    elif update.message.text and update.message.text == '/start-fresh':
        user_interview.interview_answers = {}
        user_interview.google_table_row = None
        user_interview.step = InterviewStep.start.value
        user_interview.save()

    if user_interview.step == InterviewStep.start.value:
        step_start(user_interview, bot)
    elif user_interview.step == InterviewStep.start_1.value:
        step_start_1(user_interview, bot, update)
    elif user_interview.step == InterviewStep.start_2.value:
        step_start_2(user_interview, bot, update)
    elif user_interview.step == InterviewStep.start_3.value:
        step_start_3(user_interview, bot, update)
    elif user_interview.step == InterviewStep.start_4.value:
        step_start_4(user_interview, bot, update)
    elif user_interview.step == InterviewStep.start_end.value:
        step_start_end(user_interview, bot, update)
    elif user_interview.step == InterviewStep.surname.value:
        step_surname(user_interview, bot, update)
    elif user_interview.step == InterviewStep.name.value:
        step_name(user_interview, bot, update)
    elif user_interview.step == InterviewStep.patronymic.value:
        step_patronymic(user_interview, bot, update)
    elif user_interview.step == InterviewStep.date_of_birth.value:
        step_date_of_birth(user_interview, bot, update)
    elif user_interview.step == InterviewStep.gender.value:
        step_gender(user_interview, bot, update)
    elif user_interview.step == InterviewStep.photo.value:
        step_photo(user_interview, bot, update)
    elif user_interview.step == InterviewStep.phone_number.value:
        step_phone_number(user_interview, bot, update)
    elif user_interview.step == InterviewStep.email.value:
        step_email(user_interview, bot, update)
    elif user_interview.step == InterviewStep.social_networks.value:
        step_social_networks(user_interview, bot, update)
    elif user_interview.step == InterviewStep.adm_okr.value:
        step_adm_okr(user_interview, bot, update)
    elif user_interview.step == InterviewStep.education.value:
        step_education(user_interview, bot, update)
    elif user_interview.step == InterviewStep.place_education.value:
        step_place_education(user_interview, bot, update)
    elif user_interview.step == InterviewStep.place_education_2.value:
        step_place_education_2(user_interview, bot, update)
    elif user_interview.step == InterviewStep.place_education_stop.value:
        step_place_education_stop(user_interview, bot, update)
    elif user_interview.step == InterviewStep.napr_education.value:
        step_napr_education(user_interview, bot, update)
    elif user_interview.step == InterviewStep.doc_education.value:
        step_doc_education(user_interview, bot, update)
    elif user_interview.step == InterviewStep.add_education.value:
        step_add_education(user_interview, bot, update)
    elif user_interview.step == InterviewStep.work_experience.value:
        step_work_experience(user_interview, bot, update)
    elif user_interview.step == InterviewStep.job_title.value:
        step_job_title(user_interview, bot, update)
    elif user_interview.step == InterviewStep.add_work.value:
        step_add_work(user_interview, bot, update)
    elif user_interview.step == InterviewStep.achievements.value:
        step_achievements(user_interview, bot, update)
    elif user_interview.step == InterviewStep.prof_skills.value:
        step_prof_skills(user_interview, bot, update)
    elif user_interview.step == InterviewStep.pers_qualities.value:
        step_pers_qualities(user_interview, bot, update)
    elif user_interview.step == InterviewStep.exp_children.value:
        step_exp_children(user_interview, bot, update)
    elif user_interview.step == InterviewStep.ed_oo_work.value:
        step_ed_oo_work(user_interview, bot, update)
    elif user_interview.step == InterviewStep.ed_oo_work.value:
        step_ed_oo_work(user_interview, bot, update)
    elif user_interview.step == InterviewStep.add_adm_okr.value:
        step_add_adm_okr(user_interview, bot, update)
    elif user_interview.step == InterviewStep.test.value:
        text = update.message.text.encode('utf-8').decode()
        test_step(user_interview, bot, text)
    elif user_interview.step == InterviewStep.start_test.value:
        start_user_test(user_interview, bot, update)
    elif user_interview.step == InterviewStep.finish_end.value:
        finish_end(user_interview, bot, update)


def finish_end(user_interview: Interview, bot: Bot, update: Update):
    if update.message.text:
        text = update.message.text.encode('utf-8').decode()
        if 'http' in text:
            user_interview.video_url = text
            user_interview.update_step(InterviewStep.end)
            user_interview.save_video_url_to_table()
            message = '''
👍Спасибо!

🎦Ваше видео поступило на проверку организаторам конкурса.

Пожалуйста, ожидайте результатов. 

📞Просим обратить внимание, что с Вами может связаться Организатор.

💬Сообщение о результатах и дальнейших действиях придет в этот диалог.'''
            bot.send_message(
                chat_id=user_interview.chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
            )
            return

        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Неверный формат. Прочтите инструкцию выше.',
            parse_mode=ParseMode.HTML,
        )

    bot.send_message(
        chat_id=user_interview.chat_id,
        text='Обращаем внимание, что ответным сообщением здесь необходимо прислать ссылку на видеоролик, а не сам видеоролик!',
        parse_mode=ParseMode.HTML,
    )



def start_user_test(user_interview: Interview, bot: Bot, update: Update = ''):
    text = update.message.text.encode('utf-8').decode()
    if text != 'Начать тестирование':
        return

    question_list = Questions.get_questions_list()
    user_test_list = dict()
    for idx, question in enumerate(question_list):
        user_test_list.setdefault(idx, {
            'questing_id': question.questing_id,
            'block_name': question.block_name,
            'questing_text': question.questing_text,
            'answer_one_text': question.answer_one_text,
            'answer_one_balls': question.answer_one_balls,
            'answer_two_text': question.answer_two_text,
            'answer_two_balls': question.answer_two_balls,
            'answer_three_text': question.answer_three_text,
            'answer_three_balls': question.answer_three_balls,
            'answer_four_text': question.answer_four_text,
            'answer_four_balls': question.answer_four_balls,
            'answer_five_text': question.answer_five_text,
            'answer_five_balls': question.answer_five_balls,
            'answer_count': question.answer_count,
            'try_count': 0,
            'balls': 0
        })
    finish_time = datetime.now() + timedelta(minutes=60)
    user_interview.test_finish_time = finish_time
    user_interview.questing_balls = 0
    user_interview.questing_step = -1
    user_interview.questing_text = json.loads(json.dumps(user_test_list))
    user_interview.save()
    user_interview.update_step(InterviewStep.test)
    test_step(user_interview, bot, '')


def test_step(user_interview: Interview, bot: Bot, text: str = ''):
    question_list = dict(user_interview.questing_text)
    if len(text) > 100:
        text = text.replace('…', '')
    message_text = ''
    finish_time = user_interview.test_finish_time

    if finish_time.timestamp() < datetime.now().timestamp():
        user_interview.save_test_result_to_table()
        user_interview.update_step(InterviewStep.finish)
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=f"Время выполнения теста закончилось. Ваш результат сохранен.",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        return
    if user_interview.questing_step == -1:
        message_text += 'Добрый день! \n' \
                        'Тест необходимо закончить до ' + finish_time.strftime('%Y-%m-%d %H:%M:%S') + '\n\n'
        user_interview.questing_step += 1

        question = DefaultMunch.fromDict(question_list[f'{user_interview.questing_step}'])
        message_text += f'Вопрос №{user_interview.questing_step + 1}:\n{question.questing_text}'
        if question.answer_count > 1:
            message_text += f'\nВыберите {question.answer_count} вариантов из списка'
    else:
        question = DefaultMunch.fromDict(question_list[f'{user_interview.questing_step}'])
        if len(text) > 100 and not question.answer_one_text.startswith(text) \
                and not question.answer_two_text.startswith(text) \
                and not question.answer_three_text.startswith(text) \
                and not question.answer_four_text.startswith(text) \
                and not question.answer_five_text.startswith(text):
            bot.send_message(
                chat_id=user_interview.chat_id,
                text='Воспользуйтесь кнопками ⬇',
                parse_mode=ParseMode.HTML,
            )
            return
        elif not question.answer_one_text != text \
                and not question.answer_two_text != text \
                and not question.answer_three_text != text \
                and not question.answer_four_text != text \
                and not question.answer_five_text != text:
            bot.send_message(
                chat_id=user_interview.chat_id,
                text='Воспользуйтесь кнопками ⬇',
                parse_mode=ParseMode.HTML,
            )
            return

        if question.answer_one_text.startswith(text) and question.answer_one_balls == 1:
            question.balls += 1
            question_list[f'{user_interview.questing_step}']['balls'] += 1
        elif question.answer_two_text.startswith(text) and question.answer_two_balls == 1:
            question.balls += 1
            question_list[f'{user_interview.questing_step}']['balls'] += 1
        elif question.answer_three_text.startswith(text) and question.answer_three_balls == 1:
            question.balls += 1
            question_list[f'{user_interview.questing_step}']['balls'] += 1
        elif question.answer_four_text.startswith(text) and question.answer_four_balls == 1:
            question.balls += 1
            question_list[f'{user_interview.questing_step}']['balls'] += 1
        elif question.answer_five_text.startswith(text) and question.answer_five_balls == 1:
            question.balls += 1
            question_list[f'{user_interview.questing_step}']['balls'] += 1

        question.try_count += 1
        question_list[f'{user_interview.questing_step}']['try_count'] += 1

    if question.try_count >= question.answer_count:
        if question.balls == question.answer_count:
            user_interview.questing_balls += 1

        user_interview.questing_step += 1
        if user_interview.questing_step >= len(question_list):
            user_interview.save_test_result_to_table()
            user_interview.update_step(InterviewStep.finish)
            bot.send_message(
                chat_id=user_interview.chat_id,
                text=f"Спасибо, Вы закончили тестирование.Ваша анкета и результаты тестирования поступили на проверку организаторам конкурса." \
                     f"Ожидайте, пожалуйста, приглашения ко второму этапу: творческому заданию в этом чат-боте." \
                     f"Просим обратить внимание, что с Вами может связаться Организатор для уточнения данных, указанных в анкете." ,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove()
            )
            return

        question = DefaultMunch.fromDict(question_list[f'{user_interview.questing_step}'])
        message_text += f'Вопрос №{user_interview.questing_step + 1}:\n{question.questing_text}'
        if question.answer_count > 1:
            message_text += f'\nВыберите {question.answer_count} вариантов из списка'
    elif question.try_count != 0 and question.try_count != question.answer_count:
        user_interview.questing_text = question_list
        user_interview.save()
        return

    user_interview.questing_text = question_list
    user_interview.save()

    first_line_markup = []
    second_line_markup = []
    third_line_markup = []
    if question.answer_one_text is not None and question.answer_one_text != '':
        first_line_markup.append(KeyboardButton(text=question.answer_one_text))
    if question.answer_two_text is not None and question.answer_two_text != '':
        first_line_markup.append(KeyboardButton(text=question.answer_two_text))
    if question.answer_three_text is not None and question.answer_three_text != '':
        second_line_markup.append(KeyboardButton(text=question.answer_three_text))
    if question.answer_four_text is not None and question.answer_four_text != '':
        second_line_markup.append(KeyboardButton(text=question.answer_four_text))
    if question.answer_five_text is not None and question.answer_five_text != '':
        third_line_markup.append(KeyboardButton(text=question.answer_five_text))

    keyboard_markup = []
    if len(first_line_markup) > 0:
        keyboard_markup.append(first_line_markup)
    if len(second_line_markup) > 0:
        keyboard_markup.append(second_line_markup)
    if len(third_line_markup) > 0:
        keyboard_markup.append(third_line_markup)

    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(keyboard_markup)
    )


def step_start(user_interview: Interview, bot: Bot):
    text = f"Здравствуйте, уважаемый кандидат на должность советника директора по" \
           f" воспитанию и взаимодействию с детскими общественными объединениями!\n\n" \
           f"Для участия в конкурсе Вам необходимо внести Ваши данные в этом чат-боте\n\n" \
           f"Для начала, пожалуйста,\n\n" \
           f"- ознакомьтесь с <a href='https://patriotsport.moscow/wp-content/uploads/2022/11/dc99d9d1-794b-4b98-bd1f-56c4565229ca.pdf'>Положением о конкурсе</a>\n\n" \
           f"- дайте свое согласие на <a href='https://patriotsport.moscow/wp-content/uploads/2022/03/pril-3.pdf'>" \
           f"обработку и использование персональных данных</a>👇\n\n"

    keyboard_markup = [
        [KeyboardButton(text='С положением ознакомлен')]
    ]
    with open('uploads/Patri.jpeg', 'rb') as photo:
        bot.send_photo(user_interview.chat_id, photo, caption=text, reply_markup=ReplyKeyboardMarkup(keyboard_markup),
                       parse_mode=ParseMode.HTML)
        user_interview.update_step(InterviewStep.start_1)


def step_start_1(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'С положением ознакомлен':
        keyboard_markup = [
            [KeyboardButton(text='Даю согласие на обработку и использование персональных данных')]
        ]
        message_text = 'Дайте согласие на обработку и использование персональных данных👇'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
        user_interview.update_step(InterviewStep.start_2)


def step_start_2(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Даю согласие на обработку и использование персональных данных':
        message_text = "Спасибо!\n\n " \
                       "Прежде чем приступить к заполнению анкеты, подготовьте, " \
                       "пожалуйста, «сканы» или фото следующих документов в разборчивом виде:\n\n " \
                       "- документы об образовании (диплом (главный разворот), " \
                       "свидетельство о профессиональной переподготовке (при наличии))\n\n " \
                       "- вашу фотографию для анкеты\n\n" \
                       "Все документы необходимо будет загрузить в соответствующие поля чат-бота.\n\n" \
                       "Заполнение анкеты займет у Вас около 30 минут.\n\n" \
                       "Нажмите кнопку «Правила заполнения», чтобы ознакомиться с правилами.\n\n"
        keyboard_markup = [
            [KeyboardButton(text='Правила заполнения')]
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
        user_interview.update_step(InterviewStep.start_3)


def step_start_3(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Правила заполнения':
        message_text = "Для заполнения анкеты Вам необходимо последовательно отвечать на вопросы и вводить Ваши " \
                       "данные в поле ответа на поступающие Вам сообщения в этот чат.\n\n" \
                       "Обратите внимание, что ответы на некоторые вопросы ограничены по количеству знаков " \
                       "(это будет указано в самом вопросе).\n\n" \
                       "При загрузке материалов и изображений обращайте внимание на необходимый формат файла.\n\n" \
                       "Если при заполнении вы обнаружите, что допустили ошибку или хотите изменить внесенную " \
                       "информацию, вы можете вернуться в какой-либо раздел, нажав на кнопку «меню» и выбрав " \
                       "соответствующий пункт. После внесения изменений необходимо нажать «Назад» для возврата. "
        keyboard_markup = [
            [KeyboardButton(text='Все понятно')]
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
        user_interview.update_step(InterviewStep.start_4)


def step_start_4(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Все понятно':
        message_text = 'Для начала нажмите "Старт"'
        keyboard_markup = [
            [KeyboardButton(text='Старт')]
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
        user_interview.update_step(InterviewStep.start_end)


def step_start_end(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Старт':
        message_text = 'Блок основная информация'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        message_text = 'Введите Вашу ФАМИЛИЮ'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        user_interview.update_step(InterviewStep.surname)


def step_surname(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['surname'] = text
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.name)
    message_text = 'Введите Ваше ИМЯ'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_name(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['name'] = text
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.patronymic)
    message_text = 'Введите Ваше ОТЧЕСТВО'
    keyboard_markup = [
        [KeyboardButton(text='Пропустить')]
    ]
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(keyboard_markup)
    )


def step_patronymic(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['patronymic'] = text if text != 'Пропустить' else ''
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.date_of_birth)
    message_text = 'Укажите дату рождения (в формате 20.12.2000 (ДД.ММ.ГГГГ))'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_date_of_birth(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    try:
        date_of_birth = datetime.strptime(text, '%d.%m.%Y')
        interview_answers = dict(user_interview.interview_answers)
        interview_answers['date_of_birth'] = str(date_of_birth.date())
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.gender)
        message_text = 'Укажите Ваш пол'
        keyboard_markup = [
            [KeyboardButton(text='Мужской'), KeyboardButton(text='Женский')]
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    except Exception:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Неверный формат даты \nПример для заполнения: <b>20.12.2000 (ДД.ММ.ГГГГ)</b>',
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )


def step_gender(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Мужской' or text == 'Женский':
        interview_answers = dict(user_interview.interview_answers)
        interview_answers['gender'] = text
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.photo)
        message_text = 'Загрузите Вашу фотографию для анкеты'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Воспользуйтесь кнопками ⬇',
            parse_mode=ParseMode.HTML,
        )


def step_photo(user_interview: Interview, bot: Bot, update: Update):
    if update.message.photo or update.message.document:
        user_photo_path = ''
        if update.message.document:
            file_id = update.message.document.file_id
            file: File = bot.getFile(file_id)
            user_photo_path = f'uploads/advisors/{user_interview.chat_id}/user_photo{Path(file.file_path).suffix}'
            file_buf = file.download_as_bytearray()
            default_storage.save(user_photo_path, ContentFile(file_buf))
            pass
        elif update.message.photo:
            file_id = update.message.photo[-1].file_id
            file: File = bot.getFile(file_id)
            user_photo_path = f'uploads/advisors/{user_interview.chat_id}/user_photo{Path(file.file_path).suffix}'
            file_buf = file.download_as_bytearray()
            default_storage.save(user_photo_path, ContentFile(file_buf))

        interview_answers = dict(user_interview.interview_answers)
        interview_answers['photo'] = user_photo_path
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.phone_number)

        message_text = 'Укажите Ваш номер телефона (без знаков и пробелов)\n\n' \
                       'Или нажмите кнопку <b>"Отправить телефон"</b>'
        keyboard_markup = [
            [KeyboardButton(text='Отправить телефон', request_contact=True)]
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Загрузите Вашу фотографию для анкеты',
            parse_mode=ParseMode.HTML,
        )


def step_phone_number(user_interview: Interview, bot: Bot, update: Update):
    if update.message.contact:
        interview_answers = dict(user_interview.interview_answers)
        interview_answers['phone_number'] = update.message.contact.phone_number
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.email)
        message_text = 'Укажите Ваш Email адрес'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        try:
            text = update.message.text.encode('utf-8').decode()
            if len(text) < 10 or len(text) > 11 or not text.isdigit():
                raise Exception()
            interview_answers = dict(user_interview.interview_answers)
            interview_answers['phone_number'] = text
            user_interview.interview_answers = interview_answers
            user_interview.update_step(InterviewStep.email)
            message_text = 'Укажите Ваш Email адрес'
            bot.send_message(
                chat_id=user_interview.chat_id,
                text=message_text,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception:
            bot.send_message(
                chat_id=user_interview.chat_id,
                text='Неверный формат телефона\nПример для заполнения: <b>89998883344 или 9998883344</b>',
                parse_mode=ParseMode.HTML,
            )


def step_email(user_interview: Interview, bot: Bot, update: Update):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    try:
        text = update.message.text.encode('utf-8').decode()
        if not re.fullmatch(regex, text):
            raise Exception()
        interview_answers = dict(user_interview.interview_answers)
        interview_answers['email'] = text
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.social_networks)
        message_text = 'Укажите ссылку на ОСНОВНУЮ личную страницу в социальной сети (VK, Одноклассники и др).' \
                       '\nПри отсутствии, нажмите кнопку «Пропустить»'
        keyboard_markup = [
            [KeyboardButton(text='Пропустить')]
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    except Exception:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Неверный формат электронной почты',
            parse_mode=ParseMode.HTML,
        )


def step_social_networks(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['social_networks'] = text if text != 'Пропустить' else ''
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.education)
    message_text = 'Блок образование'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
    message_text = 'Укажите уровень Вашего образования'
    keyboard_markup = [
        [
            KeyboardButton(text='Высшее (бакалавриат)'),
            KeyboardButton(text='Высшее (специалитет)'),
        ],
        [
            KeyboardButton(text='Высшее (магистратура)'),
            KeyboardButton(text='Аспирантура'),
        ],
        [
            KeyboardButton(text='Неоконченное высшее (выпускной курс)'),
        ]
    ]
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(keyboard_markup)
    )


def step_education(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Высшее (бакалавриат)' or text == 'Высшее (специалитет)' or text == 'Высшее (магистратура)' \
            or text == 'Аспирантура' or text == 'Неоконченное высшее (выпускной курс)':
        interview_answers = dict(user_interview.interview_answers)
        interview_answers['education_level'] = text
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.place_education)
        message_text = 'Выберите последнюю полученную Вами форму образования, по педагогическому профилю'
        keyboard_markup = [
            [
                KeyboardButton(text='Высшее (бакалавриат)'),
                KeyboardButton(text='Высшее (специалитет)'),
            ],
            [
                KeyboardButton(text='Высшее (магистратура)'),
                KeyboardButton(text='Аспирантура'),
            ],
            [
                KeyboardButton(text='Неоконченное высшее (выпускной курс по педагогическому направлению)'),
                KeyboardButton(text='Среднее профессиональное образование'),
            ],
            [
                KeyboardButton(text='Курсы профессиональной переподготовки/ повышения квалификации'),
            ]
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text="Воспользуйтесь кнопками ⬇️",
            parse_mode=ParseMode.HTML,
        )


def step_place_education(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Высшее (бакалавриат)' or text == 'Высшее (специалитет)' or text == 'Высшее (магистратура)' \
            or text == 'Аспирантура' or text == 'Неоконченное высшее (выпускной курс по педагогическому направлению)' \
            or text == 'Курсы профессиональной переподготовки/ повышения квалификации' \
            or text == 'Среднее профессиональное образование':
        interview_answers = dict(user_interview.interview_answers)
        interview_answers['place_education'] = text
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.place_education_2)
        message_text = 'Укажите информацию обо всех учебных заведениях (СПО, ВО), где Вы обучались.\n\n' \

        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        message_text = 'В данной графе 👇 введите название последнего учебного заведения.' \

        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text="Воспользуйтесь кнопками ⬇️",
            parse_mode=ParseMode.HTML,
        )


def step_place_education_2(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)

    if interview_answers.get('education_count'):
        education_count = interview_answers.get('education_count') + 1
    else:
        education_count = 1

    if interview_answers.get('education_list'):
        education_list = dict(interview_answers.get('education_list'))
        education_list[f'{education_count}'] = {
            'place_education': '',
            'napr_education': '',
            'place_education_stop': '',
            'doc_education': ''
        }
    else:
        education_list = dict()
        education_list[f'{education_count}'] = {
            'place_education': '',
            'napr_education': '',
            'place_education_stop': '',
            'doc_education': ''
        }
    education_list[f'{education_count}']['place_education'] = text
    interview_answers['education_count'] = education_count
    interview_answers['education_list'] = education_list
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.napr_education)
    message_text = 'Введите направление подготовки/специальности'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_napr_education(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    education_count = interview_answers.get('education_count')
    education_list = dict(interview_answers.get('education_list'))
    education_list[f'{education_count}']['napr_education'] = text
    interview_answers['education_list'] = education_list
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.place_education_stop)
    message_text = 'Укажите год окончания'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_place_education_stop(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    education_count = interview_answers.get('education_count')
    education_list = dict(interview_answers.get('education_list'))
    education_list[f'{education_count}']['place_education_stop'] = text
    interview_answers['education_list'] = education_list
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.doc_education)
    message_text = 'Загрузите документы об образовании (без приложения) и повышении квалификации (формат PDF)'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_doc_education(user_interview: Interview, bot: Bot, update: Update):
    if update.message.photo or update.message.document:
        doc_education = ''
        interview_answers = dict(user_interview.interview_answers)
        education_count = interview_answers.get('education_count')
        education_list = dict(interview_answers.get('education_list'))

        if update.message.document:
            file_id = update.message.document.file_id
            file: File = bot.getFile(file_id)
            doc_education = f'uploads/advisors/{user_interview.chat_id}/doc_education/{education_count}{Path(file.file_path).suffix}'
            file_buf = file.download_as_bytearray()
            default_storage.save(doc_education, ContentFile(file_buf))
            pass
        elif update.message.photo:
            file_id = update.message.photo[-1].file_id
            file: File = bot.getFile(file_id)
            doc_education = f'uploads/advisors/{user_interview.chat_id}/doc_education/{education_count}{Path(file.file_path).suffix}'
            file_buf = file.download_as_bytearray()
            default_storage.save(doc_education, ContentFile(file_buf))

        education_list[f'{education_count}']['doc_education'] = doc_education
        interview_answers['education_list'] = education_list
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.add_education)

        message_text = 'Добавить еще место обучения?'
        keyboard_markup = [[
            KeyboardButton(text='Добавить место обучения'),
            KeyboardButton(text='Продолжить')
        ]]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Загрузите документы об образовании (без приложения) и повышении квалификации (формат PDF)',
            parse_mode=ParseMode.HTML,
        )


def step_add_education(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Добавить место обучения':
        user_interview.update_step(InterviewStep.place_education_2)
        message_text = 'В данной графе 👇 введите название учебного заведения.'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    elif text == 'Продолжить':
        user_interview.update_step(InterviewStep.work_experience)
        message_text = 'Блок информация о трудовой деятельности'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
        message_text = 'Укажите опыт Вашей трудовой деятельности за последние 5 лет. ' \
                       'В данной графе👇 укажите название организации, являющейся вашим последним ' \
                       'или текущим местом работы.'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Воспользуйтесь кнопками ⬇',
            parse_mode=ParseMode.HTML,
        )


def step_work_experience(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)

    if interview_answers.get('work_count'):
        work_count = interview_answers.get('work_count') + 1
    else:
        work_count = 1

    if interview_answers.get('work_list'):
        work_list = dict(interview_answers.get('work_list'))
        work_list[f'{work_count}'] = {
            'work_experience': '',
            'job_title': '',
        }
    else:
        work_list = dict()
        work_list[f'{work_count}'] = {
            'work_experience': '',
            'job_title': '',
        }
    work_list[f'{work_count}']['work_experience'] = text
    interview_answers['work_count'] = work_count
    interview_answers['work_list'] = work_list
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.job_title)
    message_text = 'Укажите вашу должность'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_job_title(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)

    work_count = interview_answers.get('work_count')
    work_list = dict(interview_answers.get('work_list'))
    work_list[f'{work_count}']['job_title'] = text
    interview_answers['work_list'] = work_list
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.add_work)

    message_text = 'Хотите добавить место работы?'
    keyboard_markup = [[
        KeyboardButton(text='Добавить место работы'),
        KeyboardButton(text='Продолжить')
    ]]
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(keyboard_markup)
    )


def step_add_work(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Добавить место работы':
        user_interview.update_step(InterviewStep.work_experience)
        message_text = 'Укажите опыт Вашей трудовой деятельности за последние 5 лет. ' \
                       'В данной графе👇 укажите название организации, являющейся вашим последним ' \
                       'или текущим местом работы.'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    elif text == 'Продолжить':
        user_interview.update_step(InterviewStep.prof_skills)
        message_text = 'Перечислите Ваши профессиональные навыки (до 500 знаков).\n\n' \
                       '<i>Пример: организация мероприятий, проведение уроков, написание текстов и т.д.</i>'
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Воспользуйтесь кнопками ⬇',
            parse_mode=ParseMode.HTML,
        )


def step_prof_skills(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['prof_skills'] = text
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.pers_qualities)
    message_text = 'Перечислите Ваши личностные качества (до 500 знаков).\n\n' \
                   '<i>Пример: коммуникабельность, стрессоустойчивость и т.д.</i>'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_pers_qualities(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['pers_qualities'] = text
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.achievements)
    message_text = 'Укажите информацию о ваших достижениях (перечень опубликованных статей, реализованных проектов,' \
                   ' полученных грантов, победы в конкурсах). ' \
                   'Прикрепите ссылки на описания проектов/публикаций (при наличии). \n Объем сообщения – до 1500 знаков.'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_achievements(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['achievements'] = text
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.exp_children)
    message_text = 'Опишите опыт работы с детским коллективом (вожатская, волонтерская, преподавательская и иная ' \
                   'деятельность). \n Объем сообщения – до 1500 знаков.'
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


def step_exp_children(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['exp_children'] = text
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.ed_oo_work)
    message_text = 'Пожалуйста, укажите образовательную организацию, в которой ' \
                   'Вы планируете работать Советником (одна ОО) или нажмите «Пропустить»'
    keyboard_markup = [[
        KeyboardButton(text='Пропустить')
    ]]
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(keyboard_markup)
    )


def step_ed_oo_work(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    interview_answers = dict(user_interview.interview_answers)
    interview_answers['ed_oo_work'] = text if text != 'Пропустить' else ''
    user_interview.interview_answers = interview_answers
    user_interview.update_step(InterviewStep.adm_okr)
    message_text = 'Пожалуйста, выберите административный(е) округ(а), в котором(ых) Вы хотели бы работать Советником'
    keyboard_markup = [
        [
            KeyboardButton(text='ЦАО'),
            KeyboardButton(text='СВАО'),
            KeyboardButton(text='ВАО'),
        ],
        [
            KeyboardButton(text='ЮВАО'),
            KeyboardButton(text='ЗАО'),
            KeyboardButton(text='СЗАО'),
        ],
        [
            KeyboardButton(text='ЮЗАО'),
            KeyboardButton(text='ЮАО'),
            KeyboardButton(text='САО'),
        ],
        [
            KeyboardButton(text='ЗелАО'),
            KeyboardButton(text='ТиНАО'),
        ],
    ]
    bot.send_message(
        chat_id=user_interview.chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(keyboard_markup)
    )


def step_adm_okr(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'ЦАО' or text == 'СВАО' or text == 'ВАО' or text == 'ЮВАО' or text == 'ЗАО' or text == 'СЗАО' \
            or text == 'ЮЗАО' or text == 'ЮАО' or text == 'САО' or text == 'ЗелАО' or text == 'ТиНАО':
        interview_answers = dict(user_interview.interview_answers)
        if interview_answers.get('adm_okr_list'):
            adm_okr_list = list(interview_answers.get('adm_okr_list'))
        else:
            adm_okr_list = list()
        adm_okr_list.append(text)

        interview_answers['adm_okr_list'] = adm_okr_list
        user_interview.interview_answers = interview_answers
        user_interview.update_step(InterviewStep.add_adm_okr)

        message_text = 'Хотите добавить административный округ, в котором Вы хотели бы работать Советником?'
        keyboard_markup = [[
            KeyboardButton(text='Добавить административный округ'),
            KeyboardButton(text='Продолжить')
        ]]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Воспользуйтесь кнопками ⬇',
            parse_mode=ParseMode.HTML,
        )


def step_add_adm_okr(user_interview: Interview, bot: Bot, update: Update):
    text = update.message.text.encode('utf-8').decode()
    if text == 'Добавить административный округ':
        user_interview.update_step(InterviewStep.adm_okr)
        message_text = 'Пожалуйста, выберите административный(е) округ(а), в котором(ых) Вы хотели бы работать Советником'
        keyboard_markup = [
            [
                KeyboardButton(text='ЦАО'),
                KeyboardButton(text='СВАО'),
                KeyboardButton(text='ВАО'),
            ],
            [
                KeyboardButton(text='ЮВАО'),
                KeyboardButton(text='ЗАО'),
                KeyboardButton(text='СЗАО'),
            ],
            [
                KeyboardButton(text='ЮЗАО'),
                KeyboardButton(text='ЮАО'),
                KeyboardButton(text='САО'),
            ],
            [
                KeyboardButton(text='ЗелАО'),
                KeyboardButton(text='ТиНАО'),
            ],
        ]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    elif text == 'Продолжить':
        user_interview.save_interview_answers_to_table()
        user_interview.update_step(InterviewStep.start_test)
        message_text = 'Спасибо! Ваши данные отправлены на модерацию.\n\n ' \
                       'Теперь Вам доступно прохождение теста.\n ' \
                       'Обратите внимание, на выполнения теста даётся 60 минут'
        keyboard_markup = [[
            KeyboardButton(text='Начать тестирование'),
        ]]
        bot.send_message(
            chat_id=user_interview.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard_markup)
        )
    else:
        bot.send_message(
            chat_id=user_interview.chat_id,
            text='Воспользуйтесь кнопками ⬇',
            parse_mode=ParseMode.HTML,
        )
