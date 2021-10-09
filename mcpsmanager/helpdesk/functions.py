import gspread
from django.conf import settings
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from datetime import datetime
from .models import Employee, Message


def get_spreadsheet():
    gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key(settings.GOOGLE_HELPDESK_SPREADSHEET_ID)
    return spreadsheet.worksheet('Заявки')


def get_spreadsheet_row_values(row_number=None):
    """Getting a line in a sheet by line number or order number

    :param row_number: line number in the sheet (default None)
    :return: list of columns in a row

    """
    sheet = get_spreadsheet()
    row = list()
    if row_number:
        row = sheet.row_values(row_number)
    return [row[index] if len(row) > index else '-' for index in range(14)]


def get_spreadsheet_all_row():
    """Getting all the rows in a sheet

    :return: list of rows with columns
    """
    sheet = get_spreadsheet()
    rows = sheet.get_all_values()
    rows.pop(0)
    return [[row[index] if len(row) > index else '-' for index in range(14)] for row in rows]


def update_cell_range_on_request_number(request_number, cell_range, update_data):
    rows = get_spreadsheet_all_row()
    for idx, row in enumerate(rows):
        if row[1] != request_number:
            continue

        row_number = idx + 1
        sheet = get_spreadsheet()
        sheet.update(cell_range.format(row_number=row_number), update_data)
        break


def send_telegram_report(body_text, chat_id=None):
    """Sending a message with the delete message button

    :param body_text: message text
    :param chat_id: telegram chat id (default None). If the chat id is None,
    then all users with the is_send_report property will be found
    """
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    inline_keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')]]
    )

    if chat_id:
        bot.send_message(
            chat_id=chat_id,
            text=body_text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_keyboard_markup
        )
        return

    employees = Employee.objects.filter(is_send_report=True)

    for employee in employees:
        bot.send_message(
            chat_id=employee.chat_id,
            text=body_text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_keyboard_markup
        )


def do_report(update: Update, _):
    update.message.reply_text(
        text='Отчеты',
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text='Отчет по незавершенным заявкам', callback_data='report_on_current_request'),
                InlineKeyboardButton(text='Отчет со статистикой', callback_data='report_on_statistics'),
            ]]
        )
    )


def report_on_current_request(update: Update, _):
    """Report on incomplete requests"""
    rows = get_spreadsheet_all_row()

    not_implementer_request_list = list()
    process_request_list = list()

    for row in rows:
        if row[9] == '':
            not_implementer_request_list.append(row)
        elif row[11] != 'Выполнено' and row[11] != 'Не выполнено':
            process_request_list.append(row)

    body_text = '<b>Отчет по незавершенным заявкам</b>\n'

    if len(process_request_list) == 0 and len(not_implementer_request_list) == 0:
        body_text += 'Нет незавершенных или заявок без исполнителя'

    if len(process_request_list) > 0:
        body_text += f'\n<b>Всего заявок в процессе: </b> {len(process_request_list)}'
        for index, row in enumerate(process_request_list):
            body_text += f'\n<b>{index + 1}. Заявка № {row[1]}</b>' \
                         f'\n<b>Категория заявки: </b><i>{row[6]}</i>' \
                         f'\n<b>Время подачи: </b><i>{row[0]}</i>' \
                         f'\n<b>Желаемое время исполнения: </b><i>{row[8]}</i>' \
                         f'\n<b>Исполнитель: </b><i>{row[9]}</i>'

    if len(not_implementer_request_list) > 0:
        body_text += f'\n<b>Всего заявок без исполнителя: </b> {len(not_implementer_request_list)}'
        for index, row in enumerate(not_implementer_request_list):
            body_text += f'\n<b>{index + 1}. Заявка № {row[1]}</b>' \
                         f'\n<b>Категория заявки: </b><i>{row[6]}</i>' \
                         f'\n<b>Время подачи: </b><i>{row[0]}</i>' \
                         f'\n<b>Желаемое время исполнения: </b><i>{row[8]}</i>'

    send_telegram_report(
        body_text=body_text,
        chat_id=update.callback_query.message.chat_id,
    )


def report_on_statistics(update: Update, _):
    """Report with statistics on requests"""

    def get_implementer_text(implementers):
        """Getting text by implementer

        :param implementers: Dictionary with personal statistics of the implementer
        :return: String with the statistics of the implementer
        """
        text = '\n<b>По исполнителям:</b>'
        for (fio, implementer_data) in implementers.items():
            text += '\n<i>{fio}</i> - {count} заявок (выполнено - {complete}{process_str})' \
                .format(fio=fio,
                        count=implementer_data['count'],
                        complete=implementer_data['complete'],
                        process_str=(';в процессе - ' + str(implementer_data['process']))
                        if implementer_data['process'] > 0 else '')
        return text

    def set_statistics(statistics, l_implementer_fio, l_is_complete, l_is_not_complete, l_is_process,
                       l_is_not_implementer):
        """Filling out a dictionary with statistics

        :param statistics: Dictionary with statistics
        :param l_implementer_fio: Initials of the implementer
        :param l_is_complete: Is it request completed
        :param l_is_not_complete: Is it request not completed
        :param l_is_process: Is it request processed
        :param l_is_not_implementer: Is it request not implementer
        """
        statistics['all_count'] += 1
        statistics['complete_count'] += l_is_complete
        statistics['not_complete_count'] += l_is_not_complete
        statistics['process_count'] += l_is_process
        statistics['not_implementer_count'] += l_is_not_implementer

        if l_implementer_fio != '':
            implementer = statistics['implementer_request_list'].pop(l_implementer_fio, None)
            if implementer:
                implementer['count'] += 1
                implementer['complete'] += l_is_complete
                implementer['not_complete'] += l_is_not_complete
                implementer['process'] += l_is_process
            else:
                implementer = dict(count=1, complete=l_is_complete, not_complete=l_is_not_complete,
                                   process=l_is_process)
            statistics['implementer_request_list'].setdefault(l_implementer_fio, implementer)
        return statistics

    rows = get_spreadsheet_all_row()

    # 'count', 'complete', 'process', 'not_complete'
    today_statistics = dict(
        all_count=0,
        complete_count=0,
        not_complete_count=0,
        not_implementer_count=0,
        process_count=0,
        implementer_request_list=dict()
    )
    all_statistics = dict(all_count=0,
                          complete_count=0,
                          not_complete_count=0,
                          not_implementer_count=0,
                          process_count=0,
                          implementer_request_list=dict())

    for row in rows:
        implementer_fio = row[9]
        is_today = False
        is_complete = 0
        is_not_complete = 0
        is_process = 0
        is_not_implementer = 0

        try:
            working_datetime = datetime.strptime(row[8], '%d.%m.%Y %H:%M:%S')
            if working_datetime and working_datetime.date() == datetime.today().date():
                is_today = True
        except ValueError:
            try:
                working_datetime = datetime.strptime(row[0], '%d.%m.%Y %H:%M:%S')
                if working_datetime and working_datetime.date() == datetime.today().date():
                    is_today = True
            except ValueError:
                is_today = False

        if implementer_fio == '':
            is_not_implementer = 1
        else:
            if row[11] == 'Выполнено':
                is_complete = 1
            elif row[11] == 'Не выполнено':
                is_not_complete = 1
            else:
                is_process = 1

        all_statistics = set_statistics(statistics=all_statistics,
                                        l_is_complete=is_complete,
                                        l_is_not_complete=is_not_complete,
                                        l_is_process=is_process,
                                        l_is_not_implementer=is_not_implementer,
                                        l_implementer_fio=implementer_fio)

        if is_today:
            today_statistics = set_statistics(statistics=today_statistics,
                                              l_is_complete=is_complete,
                                              l_is_not_complete=is_not_complete,
                                              l_is_process=is_process,
                                              l_is_not_implementer=is_not_implementer,
                                              l_implementer_fio=implementer_fio)

    body_text = '<b>Отчет за день.</b>\n' \
                '\n<b>Заявки за сегодня:</b>' \
                '\n<b>Всего:</b> {count}' \
                '\n<b>Выполнено:</b> {complete}' \
                '\n<b>В процессе:</b> {process}' \
                '\n<b>Не выполнено:</b> {not_complete}' \
                '\n<b>Без исполнителя:</b> {not_implementer}' \
        .format(count=today_statistics['all_count'],
                complete=today_statistics['complete_count'],
                process=today_statistics['process_count'],
                not_complete=today_statistics['not_complete_count'],
                not_implementer=today_statistics['not_implementer_count'])

    if len(today_statistics['implementer_request_list']):
        body_text += get_implementer_text(today_statistics['implementer_request_list'])

    body_text += '\n\n<b>Заявки за всё время:</b>' \
                 '\n<b>Всего:</b> {count}' \
                 '\n<b>Выполнено:</b> {complete}' \
                 '\n<b>В процессе:</b> {process}' \
                 '\n<b>Не выполнено:</b> {not_complete}' \
                 '\n<b>Без исполнителя:</b> {not_implementer}' \
        .format(count=all_statistics['all_count'],
                complete=all_statistics['complete_count'],
                process=all_statistics['process_count'],
                not_complete=all_statistics['not_complete_count'],
                not_implementer=all_statistics['not_implementer_count'])

    if len(all_statistics['implementer_request_list']):
        body_text += get_implementer_text(all_statistics['implementer_request_list'])

    send_telegram_report(
        body_text=body_text,
        chat_id=update.callback_query.message.chat_id,
    )


def delete_message(update: Update, _):
    update.callback_query.delete_message()


def accept_button(update: Update, _):
    message = Message.objects.filter(message_id=update.callback_query.message.message_id).get()
    update_cell_range_on_request_number(
        request_number=message.request_number,
        cell_range='J{row_number}:K{row_number}',
        update_data=[[message.telegram_employee.short_name, 'Да']]
    )


def done_button(update: Update, _):
    message = Message.objects.filter(message_id=update.callback_query.message.message_id).get()
    update_cell_range_on_request_number(
        request_number=message.request_number,
        cell_range='L{row_number}',
        update_data=[['Выполнено']]
    )
