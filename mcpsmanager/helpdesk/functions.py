import gspread
from django.conf import settings
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from datetime import datetime
from helpdesk.models import Employee, Message, Account, AccountCategory
from django.http import HttpResponse


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
        if int(row[1]) != int(request_number):
            continue
        row_number = idx + 2
        sheet = get_spreadsheet()
        sheet.update(cell_range.format(row_number=row_number), update_data)
        break


def send_telegram_report(body_text, chat_id=None, message_id=None):
    """Sending a message with the delete message button

    :param body_text: message text
    :param chat_id: telegram chat id (default None). If the chat id is None,
    :param message_id: telegram message id (default None)
    then all users with the is_send_report property will be found
    """
    bot = Bot(token=settings.TELEGRAM_MCPSIT_BOT_TOKEN)
    inline_keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')]]
    )
    if chat_id:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=body_text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_keyboard_markup
        )
        return

    employees = Employee.objects.filter(is_send_report=True)

    for employee in employees:
        bot.edit_message_text(
            chat_id=employee.chat_id,
            message_id=message_id,
            text=body_text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_keyboard_markup
        )


def report_menu(update: Update):
    """Send report button menu"""
    update.message.delete()
    update.message.reply_text(
        text='Отчеты',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Отчет по незавершенным заявкам', callback_data='report_on_current_request')],
            [InlineKeyboardButton(text='Отчет со статистикой', callback_data='report_on_statistics')]
        ])
    )


def report_on_current_request(update: Update):
    """Report on incomplete requests"""
    rows = get_spreadsheet_all_row()

    not_implementer_request_list = list()
    process_request_list = list()

    for row in rows:
        if row[9] == '':
            not_implementer_request_list.append(row)
        elif row[11] != 'Выполнено' and row[11] != 'Не выполнено':
            process_request_list.append(row)

    body_text = '<b>Отчет по незавершенным заявкам</b>'

    if len(process_request_list) == 0 and len(not_implementer_request_list) == 0:
        body_text += '\n\n<b>Нет незавершенных или заявок без исполнителя</b>'

    if len(process_request_list) > 0:
        body_text += f'\n\n<b>Всего заявок в процессе: </b> {len(process_request_list)}'
        for index, row in enumerate(process_request_list):
            body_text += f'\n<b>{index + 1}. Заявка № {row[1]}</b>' \
                         f'\n<b>Категория заявки: </b><i>{row[6]}</i>' \
                         f'\n<b>Время подачи: </b><i>{row[0]}</i>' \
                         f'\n<b>Желаемое время исполнения: </b><i>{row[8]}</i>' \
                         f'\n<b>Исполнитель: </b><i>{row[9]}</i>'

    if len(not_implementer_request_list) > 0:
        body_text += f'\n\n<b>Всего заявок без исполнителя: </b> {len(not_implementer_request_list)}'
        for index, row in enumerate(not_implementer_request_list):
            body_text += f'\n<b>{index + 1}. Заявка № {row[1]}</b>' \
                         f'\n<b>Категория заявки: </b><i>{row[6]}</i>' \
                         f'\n<b>Время подачи: </b><i>{row[0]}</i>' \
                         f'\n<b>Желаемое время исполнения: </b><i>{row[8]}</i>'

    send_telegram_report(
        body_text=body_text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id
    )
    return HttpResponse()


def report_on_statistics(update: Update):
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
        message_id=update.callback_query.message.message_id
    )
    return HttpResponse()


def delete_message(update: Update):
    update.callback_query.delete_message()


def accept_button(update: Update):
    message = Message.objects.filter(message_id=update.callback_query.message.message_id).get()
    update_cell_range_on_request_number(
        request_number=message.request_number,
        cell_range='J{row_number}',
        update_data=[[message.telegram_employee.short_name, 'Да']]
    )
    return HttpResponse()


def done_button(update: Update):
    message = Message.objects.filter(message_id=update.callback_query.message.message_id).get()
    update_cell_range_on_request_number(
        request_number=message.request_number,
        cell_range='L{row_number}',
        update_data=[['Выполнено']]
    )
    return HttpResponse()


def password_list_menu(update: Update):
    update.message.delete()

    account_categories = AccountCategory.objects.all()
    button_list = [
        [InlineKeyboardButton(
            text=account_category.name,
            callback_data=f'password_category_{account_category.id}'
        )] for account_category in account_categories]
    button_list.append([InlineKeyboardButton(text='Избранные', callback_data='password_list_favorite')])
    button_list.append([InlineKeyboardButton(text='Поиск', callback_data='password_list_search_start')])

    update.message.reply_text(
        text='Выберите категория паролей',
        reply_markup=InlineKeyboardMarkup(button_list)
    )


def password_list_category_show(update: Update):
    category_action = update.callback_query.data[len('password_category_'):]
    category_action = category_action.split('_')
    category_id = int(category_action[0])
    category = AccountCategory.objects.get(id=category_id)
    page_number = 1
    if len(category_action) > 1:
        page_number = int(category_action[1])

    pagination_accounts = Account.objects.filter(category=category_id).paginator_list()
    if page_number > pagination_accounts.num_pages:
        page_number = pagination_accounts.num_pages

    show_accounts = pagination_accounts.page(page_number)

    button_list = [
        [InlineKeyboardButton(
            text=f'{show_account.login} ({show_account.note})',
            callback_data=f'password_account_{show_account.id}_show'
        )] for show_account in show_accounts.object_list]
    menu_buttons = []
    if show_accounts.has_previous():
        menu_buttons.append(InlineKeyboardButton(
            text=f'Back (page {page_number - 1})',
            callback_data=f'password_category_{category_id}_{page_number - 1}'
        ))
    if show_accounts.has_next():
        menu_buttons.append(InlineKeyboardButton(
            text=f'Next (page {page_number + 1})',
            callback_data=f'password_category_{category_id}_{page_number + 1}'
        ))
    button_list.append(menu_buttons)
    button_list.append([InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')])
    update.callback_query.message.edit_text(
        text=f'<b>Категория {category.name}</b>\nВыберите учетную запись.',
        reply_markup=InlineKeyboardMarkup(button_list),
        parse_mode=ParseMode.HTML
    )


def password_list_search_start(update: Update):
    telegram_response = update.callback_query.message.edit_text(
        text=f'Поиск учетной записи по Login или Примечанию.\n'
             f'Для поиска отправте сообщение со словом для поиска.\n'
             f'Для завершения поиска нажмите кнопку "Завершить поиск".',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text='Завершить поиск',
                    callback_data=f'password_list_search_end'
                )
            ]
        ]),
        parse_mode=ParseMode.HTML
    )
    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)
    employee.actual_action = f'password_list_search_{telegram_response.message_id}'
    employee.save()


def password_list_search_end(update: Update):
    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)
    employee.actual_action = ''
    employee.save()
    update.callback_query.message.delete()


def password_list_search(update: Update):
    page_number = 1
    update_message = update.message
    if update.callback_query:
        update_message = update.callback_query.message
        callback_data = update.callback_query.data[len('password_list_search_'):]
        page_number = int(callback_data[:callback_data.index('_')])
        search_text = callback_data[(callback_data.index('_') + 1):]
    else:
        search_text = update.message.text

    update_message.delete()
    employee = Employee.objects.get(chat_id=update_message.chat.id)

    pagination_accounts = Account.objects.search_by_login_and_note(search_text).paginator_list()

    if page_number > pagination_accounts.num_pages:
        page_number = pagination_accounts.num_pages
    show_accounts = pagination_accounts.page(page_number)
    button_list = [
        [InlineKeyboardButton(
            text=f'{show_account.login} ({show_account.note})',
            callback_data=f'password_account_{show_account.id}_show'
        )] for show_account in show_accounts.object_list]
    menu_buttons = []
    if show_accounts.has_previous():
        menu_buttons.append(InlineKeyboardButton(
            text=f'Back (page {page_number - 1})',
            callback_data=f'password_list_search_{page_number - 1}_{search_text}'
        ))
    if show_accounts.has_next():
        menu_buttons.append(InlineKeyboardButton(
            text=f'Next (page {page_number + 1})',
            callback_data=f'password_list_search_{page_number + 1}_{search_text}'
        ))
    button_list.append(menu_buttons)
    button_list.append([InlineKeyboardButton(text='Завершить поиск', callback_data=f'password_list_search_end')])
    telegram_response = update_message.reply_text(
        text=f'Поиск учетных записей по: <b>{search_text}</b>\nВыберите учетную запись.',
        reply_markup=InlineKeyboardMarkup(button_list),
        parse_mode=ParseMode.HTML
    )

    if update.message:
        bot = Bot(token=settings.TELEGRAM_MCPSIT_BOT_TOKEN)
        bot.delete_message(chat_id=employee.chat_id,
                           message_id=int(employee.actual_action[len('password_list_search_'):]))

    employee.actual_action = f'password_list_search_{telegram_response.message_id}'
    employee.save()


def password_list_favorite(update: Update):
    page_number = update.callback_query.data[len('password_list_favorite'):]
    if page_number != '':
        page_number = int(page_number[1:])
    else:
        page_number = 1

    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)
    pagination_accounts = employee.favorite_accounts.paginator_list()

    if pagination_accounts.count < 1:
        update.callback_query.message.edit_text(
            text='<b>У вас нет избранны учетныъ записей</b>',
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')
            ]])
        )
        return

    if page_number > pagination_accounts.num_pages:
        page_number = pagination_accounts.num_pages

    show_accounts = pagination_accounts.page(page_number)

    button_list = [
        [InlineKeyboardButton(
            text=f'{show_account.login} ({show_account.note})',
            callback_data=f'password_account_{show_account.id}_show'
        )] for show_account in show_accounts.object_list]
    menu_buttons = []
    if show_accounts.has_previous():
        menu_buttons.append(InlineKeyboardButton(
            text=f'Back (page {page_number - 1})',
            callback_data=f'password_list_favorite_{page_number - 1}'
        ))
    if show_accounts.has_next():
        menu_buttons.append(InlineKeyboardButton(
            text=f'Next (page {page_number + 1})',
            callback_data=f'password_list_favorite_{page_number + 1}'
        ))
    button_list.append(menu_buttons)
    button_list.append([InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')])
    update.callback_query.message.edit_text(
        text='<b>Избранные учетные записи</b>\nВыберите учетную запись.',
        reply_markup=InlineKeyboardMarkup(button_list),
        parse_mode=ParseMode.HTML
    )


def password_account_handler(update: Update):
    callback_data = update.callback_query.data[len('password_account_'):]
    if callback_data.endswith('show'):
        account_id = int(update.callback_query.data.replace('password_account_', '').replace('_show', ''))
        password_account_show(update, account_id)
    elif callback_data.endswith('favorite_add'):
        account_id = int(update.callback_query.data.replace('password_account_', '').replace('_favorite_add', ''))
        password_account_favorite_add(update, account_id)
    elif callback_data.endswith('favorite_delete'):
        account_id = int(update.callback_query.data.replace('password_account_', '').replace('_favorite_delete', ''))
        password_account_favorite_delete(update, account_id)
    elif callback_data.endswith('edit_password_start'):
        account_id = update.callback_query.data.replace('password_account_', '').replace('_edit_password_start', '')
        password_account_edit_password_start(update, int(account_id))
    elif callback_data.endswith('edit_password_end'):
        account_id = update.callback_query.data.replace('password_account_', '').replace('_edit_password_end', '')
        password_account_edit_password_end(update, int(account_id))


def password_account_show(update: Update, account_id: int):
    account = Account.objects.get(id=account_id)
    actual = 'Нет сведений'
    if account.updated:
        actual = account.updated.strftime("%d.%m.%Y")

    button_menu = list()
    if account.employees.filter(chat_id=update.callback_query.message.chat.id):
        button_menu.append([InlineKeyboardButton(
            text='Удалить из избранных',
            callback_data=f'password_account_{account_id}_favorite_delete'
        )])
    else:
        button_menu.append([InlineKeyboardButton(
            text='Добавить в избранные',
            callback_data=f'password_account_{account_id}_favorite_add'
        )])

    button_menu.append([InlineKeyboardButton(
        text='Изменить пароль',
        callback_data=f'password_account_{account_id}_edit_password_start'
    )])
    button_menu.append([InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')])

    update.callback_query.message.reply_text(
        text=f'<b>Логин:</b> {account.login}\n'
             f'<b>Пароль:</b> {account.password}\n'
             f'<b>Описание:</b> {account.note}\n'
             f'<b>Актуально:</b> {actual}',
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(button_menu),
    )
    return


def password_account_favorite_add(update: Update, account_id: int):
    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)
    account = Account.objects.get(id=account_id)
    employee.favorite_accounts.add(account)

    update.callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text='Удалить из избранных',
                callback_data=f'password_account_{account_id}_favorite_delete'
            )],
            [InlineKeyboardButton(
                text='Изменить пароль',
                callback_data=f'password_account_{account_id}_edit_password_start'
            )],
            [InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')]
        ]),
    )
    return


def password_account_favorite_delete(update: Update, account_id: int):
    account = Account.objects.get(id=account_id)
    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)
    account.employees.remove(employee)
    update.callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text='Добавить в избранные',
                callback_data=f'password_account_{account_id}_favorite_add'
            )],
            [InlineKeyboardButton(
                text='Изменить пароль',
                callback_data=f'password_account_{account_id}_edit_password_start'
            )],
            [InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')]
        ]),
    )
    return


def password_account_edit_password_start(update: Update, account_id: int):
    account = Account.objects.get(id=account_id)
    telegram_response = update.callback_query.message.edit_text(
        text=f'Редактирование пароля учетной записи <b>{account.login}</b>\n'
             f'Старый пароль: <b>{account.password}</b>',
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text='Отмена',
                    callback_data=f'password_account_{account_id}_edit_password_end'
                )
            ]
        ]),
        parse_mode=ParseMode.HTML
    )
    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)
    employee.actual_action = f'password_account_{account_id}_{telegram_response.message_id}_edit_password'
    employee.save()
    return


def password_account_edit_password_end(update: Update, account_id: int):
    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)
    employee.actual_action = ''
    employee.save()
    update.callback_query.message.delete()
    password_account_show(update, account_id)
    return


def password_account_edit(update: Update):
    employee = Employee.objects.get(chat_id=update.message.chat.id)
    action = employee.actual_action.replace('password_account_', '').replace('_edit_password', '').split('_')
    account_id = action[0]
    message_id = action[1]
    account = Account.objects.get(id=account_id)
    account.edit_password(update.message.text)
    employee.actual_action = ''
    employee.save()
    update.message.delete()
    bot = Bot(token=settings.TELEGRAM_MCPSIT_BOT_TOKEN)
    bot.delete_message(chat_id=update.message.chat_id, message_id=message_id)
    update.message.reply_text(
        text='Пароль изменён!',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text='Удалить сообщение', callback_data='delete_message')
        ]])
    )
    return


def checklist_menu(update: Update):
    update.message.delete()
    update.message.reply_text(
        text='Автоматическое заполнение чек листа.\n'
             'Выберите адрес, после выбора адреса, форма будет отправлена автоматически',
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text='Открытое шоссе', callback_data='checklist_check_osh'),
            ]]
        )
    )


def checklist_check(update: Update, address_code: str):
    update.callback_query.delete_message()
    gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key(settings.GOOGLE_CHECKLIST_SPREADSHEET_ID)
    employee = Employee.objects.get(chat_id=update.callback_query.message.chat.id)

    # Добавление столбца в таблице адреса
    if address_code == 'osh':
        sheet = spreadsheet.worksheet('Открытое шоссе, дом 6, корпус 12')
        spreadsheet.batch_update({
            'requests': [{
                "insertDimension": {
                    "range": {
                        "sheetId": sheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": 2,
                    },
                    "inheritFromBefore": False
                },
            }]
        })

        cell_list = sheet.range('B1:B62')
        cell_values = [datetime.now().strftime("%d.%m.%Y %H:%M:%S"), employee.short_name, '', 'Работает', 'Работает',
                       'Работает', 'Работает', 'Работает', 'Работает', '', 'Работает', 'Работает', 'Работает',
                       'Работает',
                       'Работает', 'Работает', 'Работает', '', 'Работает', 'Работает', 'Работает', 'Работает', '',
                       'Работает', 'Работает', 'Работает', 'Работает', '', '', '', '', '', '', 'Работает', 'Работает',
                       'Работает', 'Работает', 'Работает', 'Работает', 'Работает', '', 'Работает', 'Работает',
                       'Работает',
                       'Работает', 'Работает', 'Работает', 'Работает', 'Работает', 'Работает', '', 'Работает',
                       'Работает',
                       'Работает', 'Работает', 'Работает', 'Работает', 'Работает', '', 'Работает', 'Работает',
                       'Работает', ]

        for i, val in enumerate(cell_values):
            cell_list[i].value = val

        sheet.update_cells(cell_list)

        # Никита, Панченко, Губин, Буздакин
        report_employees = Employee.objects.filter(is_send_report=True)
        bot = Bot(token=settings.TELEGRAM_MCPSIT_BOT_TOKEN)
        body_text = f'Произведена утренняя проверка!\nВремя: {datetime.now().strftime("%a %b %d %Y %H:%M:%S")}\n' \
                    f'Место: Ежедневная утренняя проверка оборудования\nПроверяющий: {employee.short_name}\n' \
                    f'Адрес: Открытое шоссе, дом 6, корпус 12\nПроблемы:  не обнаружены.'
        print(body_text)
        for report_employee in report_employees:
            bot.send_message(chat_id=report_employee.chat_id, text=body_text, parse_mode=ParseMode.HTML)
