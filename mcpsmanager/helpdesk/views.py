import json
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import TelegramError
from helpdesk.functions import *


def new_request(_, row_number):
    """Sending a notification about a new request"""
    row = get_spreadsheet_row_values(row_number=row_number)
    request_number = row[1]
    body_text = f'<b>Новая заявка № {request_number}</b>\n\n' \
                f'<b>Заявитель: </b> {row[2]}\n' \
                f'<b>Телефон: </b> {row[3]}\n' \
                f'<b>Адрес: </b> {row[4]}\n' \
                f'<b>Номер кабинета: </b> {row[5]}\n' \
                f'<b>Категория: </b> {row[6]}\n' \
                f'<b>Описание: </b> {row[7]}\n' \
                f'<b>Желаемое время: </b> {row[8]}'

    employees = Employee.objects.filter(is_send_new_request=True)
    inline_keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Принять', callback_data='helpdesk_accept')]]
    )
    for employee in employees:
        Message.send(employee, request_number, body_text, inline_keyboard_markup)

    return JsonResponse({'success': True})


def accept_request(_, row_number):
    """Sending a notification of the contractor's acceptance of the request"""
    row = get_spreadsheet_row_values(row_number=row_number)
    request_number = row[1]

    if row[10] != 'Да':
        return JsonResponse({'success': True})

    Message.objects.filter(request_number=request_number).delete()

    if row[11] == 'Выполнено':
        return JsonResponse({'success': True})

    body_text = f'<b>У вас новая заявка № {request_number}</b>\n\n' \
                f'<b>Заявитель: </b> {row[2]}\n' \
                f'<b>Телефон: </b> {row[3]}\n' \
                f'<b>Адрес: </b> {row[4]}\n' \
                f'<b>Номер кабинета: </b> {row[5]}\n' \
                f'<b>Категория: </b> {row[6]}\n' \
                f'<b>Описание: </b> {row[7]}\n' \
                f'<b>Желаемое время: </b> {row[8]}'

    employee = Employee.objects.get(short_name=row[9])

    if not employee:
        return JsonResponse({'success': False}, status=200)

    inline_keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Выполнено', callback_data='helpdesk_done')]]
    )
    Message.send(employee, request_number, body_text, inline_keyboard_markup)

    return JsonResponse({'success': True})


def done_request(_, row_number):
    """Sending a notification about the completion of the request"""
    row = get_spreadsheet_row_values(row_number=row_number)
    Message.objects.filter(request_number=row[1]).delete()
    return JsonResponse({'success': True})


def reminder():
    """Sending a notification with a reminder of incomplete requests"""
    rows = get_spreadsheet_all_row()
    members = dict()

    for row in rows:
        if row[9] == '' or row[11] == 'Выполнено' or row[11] == 'Не выполнено':
            continue

        employee = Employee.objects.filter(short_name=row[9]).first()
        if not employee:
            continue

        if not members.get(employee.chat_id):
            members.setdefault(employee.chat_id, 'Ваши незакрытые заявки:\n')

        members[employee.chat_id] += '\nЗаявка № {number} - дата {date}'.format(date=row[0], number=row[1])

    for (chat_id, text) in members.items():
        send_telegram_report(body_text=text, chat_id=chat_id)

    return JsonResponse({'success': True})


def import_passwords(_):
    AccountCategory.objects.import_from_google_table()
    return JsonResponse({'success': True})


@csrf_exempt
def webhook(request: WSGIRequest):
    bot = Bot(
        token=settings.TELEGRAM_MCPSIT_BOT_TOKEN
    )
    json_body = json.loads(request.body)
    update = Update.de_json(json_body, bot)
    try:
        if update.message:
            text = update.message.text.encode('utf-8').decode()

            # Команды меню
            if text == '/report':
                report_menu(update)
            elif text == '/password':
                password_list_menu(update)
            elif text == '/checklist':
                checklist_menu(update)
            else:
                # Проверка наличия у пользователя активных действий
                employee = Employee.objects.get(chat_id=update.message.chat.id)
                if employee.actual_action.startswith('password_list_search'):
                    password_list_search(update)
                elif employee.actual_action.startswith('password_account') \
                        and employee.actual_action.endswith('edit_password'):
                    password_account_edit(update)
        elif update.callback_query:
            action = update.callback_query.data

            # Обработчики меню отчетов
            if action == 'report_on_current_request':
                report_on_current_request(update)
            elif action == 'report_on_statistics':
                report_on_statistics(update)

            # Разное
            if action == 'delete_message':
                delete_message(update)

            # Обработчики меню заявок
            if action == 'helpdesk_accept':
                accept_button(update)
            elif action == 'helpdesk_done':
                done_button(update)

            # Обработчики меню чек листов
            if action == 'checklist_check_osh':
                checklist_check(update, 'osh')

            # Обработчики меню паролей
            if action == 'password_list_favorite':
                password_list_favorite(update)
            elif action == 'password_list_search_start':
                password_list_search_start(update)
            elif action == 'password_list_search_end':
                password_list_search_end(update)
            elif action.startswith('password_list_search'):
                password_list_search(update)
            elif action.startswith('password_category'):
                password_list_category_show(update)
            elif action.startswith('password_account'):
                password_account_handler(update)

    except TelegramError:
        bot.send_message(text=json_body, chat_id=332158440)
    return HttpResponse()
