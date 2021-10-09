from django.http import JsonResponse
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from .functions import get_spreadsheet_all_row, get_spreadsheet_row_values, send_telegram_report
from .models import Employee, Message


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
        [[InlineKeyboardButton(text='Принять', callback_data='accept')]]
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
        [[InlineKeyboardButton(text='Выполнено', callback_data='done')]]
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
