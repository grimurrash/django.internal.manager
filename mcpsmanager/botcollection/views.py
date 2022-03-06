import json
from json import JSONDecodeError

import gspread
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot, Update, TelegramError, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from botcollection.models import SurveyBotMessage


def save_survey_bot_info(survey_bot: SurveyBotMessage):
    def next_available_row(worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list) + 1)

    gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key('1uEeJGp8ApsMGYaKSemRGbPHg0ntlQwhEf3i3DyAizQo')
    sheet = spreadsheet.worksheet('Участники')
    next_row = next_available_row(sheet)
    sheet.update(f'A{next_row}', [
        [survey_bot.surname, survey_bot.first_name, survey_bot.last_name, survey_bot.school, survey_bot.email,
         survey_bot.arrival_method]])


@csrf_exempt
def survey_bot_webhook(request: WSGIRequest):
    bot = Bot(token='5027156115:AAFZSXQkR2Q3jI-IUi5o-PTYw45ER7vpeLI')
    try:
        json_body = json.loads(request.body)
        update = Update.de_json(json_body, bot)

        if update.message:
            text = update.message.text.encode('utf-8').decode()
            chat_id = update.message.chat.id

            if text == '/start':
                obj, created = SurveyBotMessage.objects.update_or_create(defaults={
                    'status': SurveyBotMessage.SurveyStatus.SURNAME,
                }, chat_id=chat_id)
                if created:
                    bot.send_message(chat_id=chat_id,
                                     text='Добрый день! Пожалуйста, пройдите опрос. В случае возникновения ошибок при '
                                          'заполнении полей, отправте сообщение /start, опрос начнётся заново')
                bot.send_message(chat_id=chat_id, text='Введите фамилию:')
            else:
                survey_bot = SurveyBotMessage.objects.get(chat_id=chat_id)
                if survey_bot.status == SurveyBotMessage.SurveyStatus.SURNAME:
                    survey_bot.surname = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.FIRSTNAME
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Введите имя:', )
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.FIRSTNAME:
                    survey_bot.first_name = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.LASTNAME
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Введите отчество:')
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.LASTNAME:
                    survey_bot.last_name = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.SCHOOL
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Введите наименование школы:')
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.SCHOOL:
                    survey_bot.school = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.EMAIL
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Введите электронную почту:')
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.EMAIL:
                    survey_bot.email = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.ARRIVAL_METHOD
                    survey_bot.save()
                    inline_keyboard_markup = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text='Трансфер', callback_data='arrival_method_bus')],
                         [InlineKeyboardButton(text='Самостоятельно', callback_data='arrival_method_car')]]
                    )
                    bot.send_message(chat_id=chat_id,
                                     text='Как планируете добираться?',
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=inline_keyboard_markup)
        elif update.callback_query:
            action = update.callback_query.data
            chat_id = update.callback_query.message.chat.id
            survey_bot = SurveyBotMessage.objects.get(chat_id=chat_id)
            if survey_bot.status == SurveyBotMessage.SurveyStatus.ARRIVAL_METHOD:
                if action == 'arrival_method_bus':
                    survey_bot.arrival_method = SurveyBotMessage.ArrivalMethod.BUS
                    survey_bot.status = SurveyBotMessage.SurveyStatus.END
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id,
                                     text='Спасибо!'
                                          '\n\nТрансфер до отеля будет организован от м. Аннино.'
                                          '\n<b>Сбор</b> в 7:15 15 февраля'
                                          '\n<b>Отъезд</b> 7:30 15 февраля'
                                          '\nТочка сбора: Точка сбора: Выход из метро номер 2.'
                                          '\nКонтактное лицо: +79263484222 (Уналбаева Светлана Валерьевна)',
                                     parse_mode=ParseMode.HTML),
                    bot.send_location(chat_id=chat_id, latitude=55.584325, longitude=37.596929)
                    save_survey_bot_info(survey_bot)
                elif action == 'arrival_method_car':
                    survey_bot.arrival_method = SurveyBotMessage.ArrivalMethod.CAR
                    survey_bot.status = SurveyBotMessage.SurveyStatus.END
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id,
                                     text='Уважаемые участники выезда!'
                                          '\n15 февраля 2022 года в 9:00 мы ждем вас в парк-отеле «Воздвиженское» по '
                                          'адресу: Московская область, Серпуховский район, поселок Д/О Авангард.',
                                     parse_mode=ParseMode.HTML)
                    bot.send_location(chat_id=chat_id, latitude=54.961159, longitude=37.460555)
                    save_survey_bot_info(survey_bot)
    except SurveyBotMessage.DoesNotExist:
        json_body = json.loads(request.body)
        update = Update.de_json(json_body, bot)
        chat_id = 0
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id

        obj, created = SurveyBotMessage.objects.update_or_create(defaults={
            'status': SurveyBotMessage.SurveyStatus.SURNAME,
        }, chat_id=chat_id)
        if created:
            bot.send_message(chat_id=chat_id,
                             text='Произошла ошибка при сохранении результатов опроса. Пройдите пожалуйста опрос заново.')
            bot.send_message(chat_id=chat_id, text='Введите фамилию:')
        else:
            bot.send_message(text=f'Ошибка пользователя нет!!!\n {json_body}', chat_id=332158440)
    except (ValueError, TelegramError, JSONDecodeError, Exception) as error:
        bot.send_message(text=f'{error} {json_body}', chat_id=332158440)

    return HttpResponse()
