import json
from json import JSONDecodeError

import gspread
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import *
from botcollection.models import SurveyBotMessage


def save_survey_bot_info(survey_bot: SurveyBotMessage):
    def next_available_row(worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list) + 1)

    gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key('1uEeJGp8ApsMGYaKSemRGbPHg0ntlQwhEf3i3DyAizQo')
    sheet = spreadsheet.worksheet('Участники')
    next_row = next_available_row(sheet)
    sheet.update(f'A{next_row}', [[
        survey_bot.surname,
        survey_bot.first_name,
        survey_bot.last_name,
        survey_bot.school,
        survey_bot.phone,
        survey_bot.arrival_method,
        survey_bot.car_brand,
        survey_bot.car_number
    ]])


@csrf_exempt
def survey_bot_webhook(request: WSGIRequest):
    bot = Bot(token='5728967021:AAG9XQyw4kcZqjvmC_egrXpI59WS13Vt7A4')
    try:
        json_body = json.loads(request.body)
        update = Update.de_json(json_body, bot)

        if update.message:
            if update.message.contact:
                text = update.message.contact.phone_number
            else:
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
                    bot.send_message(chat_id=chat_id, text='Введите наименование образовательной организации:')
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.SCHOOL:
                    survey_bot.school = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.PHONE
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Введите номер телефона:', reply_markup=ReplyKeyboardMarkup(
                        one_time_keyboard=True,
                        resize_keyboard=True,
                        keyboard=[[
                            KeyboardButton(text='Отправить телефон', request_contact=True),
                        ]]
                    ))
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.CAR_BRAND:
                    survey_bot.car_brand = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.CAR_NUMBER
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Введите номер автомобиля:')
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.CAR_NUMBER:
                    survey_bot.car_number = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.END
                    with open('uploads/survey_bot/car.jpg', 'rb') as photo:
                        bot.send_photo(chat_id=chat_id, photo=photo, caption='''
Уважаемые участники выезда! 
27 февраля 2023 года в 8:30 мы ждем вас в парк-отеле «Воздвиженское» по адресу: Московская область, Серпуховский район, поселок Д/О Авангард.
''',
                                       reply_markup=ReplyKeyboardRemove(),
                                       parse_mode="HTML")
                    survey_bot.save()
                    save_survey_bot_info(survey_bot)
                elif survey_bot.status == SurveyBotMessage.SurveyStatus.PHONE:
                    survey_bot.phone = text
                    survey_bot.status = SurveyBotMessage.SurveyStatus.ARRIVAL_METHOD
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Как планируете добираться?', reply_markup=ReplyKeyboardRemove())
                    inline_keyboard_markup = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text='Трансфер', callback_data='arrival_method_bus')],
                         [InlineKeyboardButton(text='Самостоятельно', callback_data='arrival_method_car')]]
                    )
                    bot.send_message(chat_id=chat_id,
                                     text='Выберите из указанных вариантов:',
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

                    with open('uploads/survey_bot/bus.jpg', 'rb') as photo:
                        bot.send_photo(chat_id=chat_id, photo=photo, caption='''
Трансфер до отеля будет организован от м. Аннино.
<b>Сбор</b> в 06:50 27 февраля 2023 года
<b>Отъезд</b> в 7:15 27 февраля 2023 года
Точка сбора: Выход из метро номер 2, далее пешком 300 метров в сторону центра, напротив дома Варшавское шоссе 154 к2
Контактное лицо: +79263484222 (Уналбаева Светлана Валерьевна)
''', reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
                    survey_bot.save()
                    save_survey_bot_info(survey_bot)
                elif action == 'arrival_method_car':
                    survey_bot.arrival_method = SurveyBotMessage.ArrivalMethod.CAR
                    survey_bot.status = SurveyBotMessage.SurveyStatus.CAR_BRAND
                    survey_bot.save()
                    bot.send_message(chat_id=chat_id, text='Введите марку автомобиля:', reply_markup=ReplyKeyboardRemove())
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
