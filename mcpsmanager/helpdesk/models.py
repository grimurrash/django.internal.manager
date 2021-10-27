import gspread
from datetime import datetime
from django.db import transaction
from django.conf import settings
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from telegram import Bot, TelegramError, ParseMode


class Employee(models.Model):
    short_name = models.CharField('Инициалы сотрудника', max_length=100)
    chat_id = models.IntegerField('Chat id пользователя телеграмм')
    is_send_new_request = models.BooleanField('Отправлять новые заявки сотруднику', default=False)
    is_send_report = models.BooleanField('Отправлять уведомления', default=False)
    actual_action = models.CharField('Активное действие', blank=True, default='', max_length=50)
    objects = models.QuerySet.as_manager()

    def __str__(self):
        return f'{self.short_name} (chatId={self.chat_id})'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['-id']


class MessageQuerySet(models.QuerySet):
    def delete(self):
        bot = Bot(token=settings.TELEGRAM_MCPSIT_BOT_TOKEN)
        for obj in self:
            try:
                bot.delete_message(chat_id=obj.telegram_employee.chat_id, message_id=obj.message_id)
            except TelegramError:
                pass
                # bot.send_message(chat_id=obj.telegram_employee.chat_id,
                #                  text=f'Не получилось удалить сообщение по заявке № {obj.request_number}. '
                #                       f'Удалите его в ручную!')

        super(MessageQuerySet, self).delete()


class Message(models.Model):
    objects = MessageQuerySet.as_manager()
    telegram_employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message_id = models.CharField('Id сообщения телеграмм', max_length=15, null=True)
    request_number = models.IntegerField('Номер заявки в HelpDesk')

    def __str__(self):
        return f'Сообщение пользователя {self.telegram_employee.short_name} по заявке {self.request_number}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-id']

    def delete(self, using=None, keep_parents=False):
        bot = Bot(token=settings.TELEGRAM_MCPSIT_BOT_TOKEN)
        try:
            bot.delete_message(chat_id=self.telegram_employee.chat_id, message_id=self.message_id)
        except TelegramError:
            bot.send_message(chat_id=self.telegram_employee.chat_id,
                             text=f'Не получилось удалить сообщение по заявке № {self.request_number}. '
                                  f'Удалите его в ручную!')

        super(Message, self).delete()

    @classmethod
    def send(cls, employee, request_number, text, reply_markup):
        bot = Bot(token=settings.TELEGRAM_MCPSIT_BOT_TOKEN)
        try:
            telegram_response = bot.send_message(chat_id=employee.chat_id,
                                                 text=text,
                                                 parse_mode=ParseMode.HTML,
                                                 reply_markup=reply_markup)
            message = cls(telegram_employee_id=employee.id, request_number=request_number,
                          message_id=telegram_response.message_id)
            message.save()
            return message
        except TelegramError:
            return None


class AccountCategoryQuerySet(models.QuerySet):
    def import_from_google_table(self):
        for account_category in self:
            account_category.import_from_google_table()


class AccountCategory(models.Model):
    name = models.CharField('Наименование категории', max_length=100)

    is_import = models.BooleanField('Импортировать из google таблицы', default=False)
    import_table_id = models.CharField('Id google таблицы', max_length=50, blank=True, default='')
    import_sheet_name = models.CharField('Наименование листа', max_length=50, blank=True, default='')

    login_field_column_number = models.IntegerField(verbose_name='Номер столбца с логином или почтой (начиная с 1)',
                                                    default=0, null=False)
    password_field_column_number = models.IntegerField('Номер столбца c паролем (начиная с 1)', default=0, null=False)
    note_field_column_number = models.IntegerField('Номер столбца c примечанием (начиная с 1)', default=0, null=False)
    updated_field_column_number = models.IntegerField('Номер столбца с датой последнего изменения пароля (начиная с 1)',
                                                      default=0, null=False)

    objects = AccountCategoryQuerySet.as_manager()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Категория учетной записи'
        verbose_name_plural = 'Категории учетных записей'
        ordering = ['-id']

    def import_from_google_table(self):
        if not self.is_import:
            return

        gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
        sheet = gc.open_by_key(str(self.import_table_id)).worksheet(str(self.import_sheet_name))
        rows = sheet.get_all_values()
        if len(rows) < 1:
            return

        rows.pop(0)
        accounts = self.account_set.all()
        update_account_categories = list()
        with transaction.atomic():
            for row in rows:
                if self.login_field_column_number == 0 or self.password_field_column_number == 0 or \
                        self.note_field_column_number == 0:
                    continue

                login = str(row[self.login_field_column_number - 1]).strip()
                if not login:
                    continue

                password = str(row[self.password_field_column_number - 1]).strip()
                note = str(row[self.note_field_column_number - 1]).strip()
                if self.updated_field_column_number == 0 or len(row) < self.updated_field_column_number:
                    updated = None
                elif row[self.updated_field_column_number - 1] == '':
                    updated = None
                else:
                    updated = datetime.strptime(row[self.updated_field_column_number - 1], '%d.%m.%Y')

                account, created = Account.objects.update_or_create(defaults={
                    'password': password,
                    'note': note,
                    'category': self,
                    'updated': updated
                }, login=login)
                if not created:
                    update_account_categories.append(account)

            delete_list = [account for account in accounts if account not in update_account_categories]
            for delete_account in delete_list:
                delete_account.delete()


class AccountQuerySet(models.QuerySet):
    def paginator_list(self) -> Paginator:
        return Paginator(self, 10)

    def search_by_login_and_note(self, search_text):
        return self.filter(Q(login__icontains=search_text) | Q(note__icontains=search_text))


class Account(models.Model):
    login = models.CharField('Логин или email', max_length=100)
    password = models.CharField('Пароль', max_length=100, blank=True)
    note = models.CharField('Примечание', default='-', max_length=255)
    category = models.ForeignKey(AccountCategory, on_delete=models.CASCADE)
    employees = models.ManyToManyField(Employee, related_name='favorite_accounts', blank=True)
    updated = models.DateField('Время последнего изменения', blank=True, null=True)
    objects = AccountQuerySet.as_manager()

    def __str__(self):
        return f'Учетная запись: {self.login} | Категория: {self.category.name} | Примечание: {self.note}'

    class Meta:
        verbose_name = 'Учетная запись'
        verbose_name_plural = 'Учетные записи'
        ordering = ['login']

    def edit_password(self, new_password: str):
        category = self.category
        if (not category.is_import) \
                or category.login_field_column_number == 0 or category.password_field_column_number == 0:
            self.password = new_password
            self.updated = datetime.now().strftime('%d.%m.%Y')
            self.save()
            return

        gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
        sheet = gc.open_by_key(str(category.import_table_id)).worksheet(str(category.import_sheet_name))

        cell_lookup = sheet.find(self.login)

        cell_list = []
        if cell_lookup:
            cell_to_update_password = sheet.cell(cell_lookup.row, category.password_field_column_number)
            cell_to_update_password.value = new_password
            cell_list.append(cell_to_update_password)

            if category.updated_field_column_number > 0:
                cell_to_update_updated_date = sheet.cell(cell_lookup.row, category.updated_field_column_number)
                cell_to_update_updated_date.value = datetime.now().strftime('%d.%m.%Y')
                cell_list.append(cell_to_update_updated_date)
            sheet.update_cells(cell_list)

        self.password = new_password
        self.updated = datetime.now().strftime('%d.%m.%Y')
        self.save()
        return
