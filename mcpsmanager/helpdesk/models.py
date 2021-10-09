from django.conf import settings
from django.db import models
from telegram import Bot, TelegramError, ParseMode


class Employee(models.Model):
    short_name = models.CharField('Инициалы сотрудника', max_length=100)
    chat_id = models.IntegerField('Chat id пользователя телеграмм')
    is_send_new_request = models.BooleanField('Отправлять новые заявки сотруднику', default=False)
    is_send_report = models.BooleanField('Отправлять отчеты по заявкам по времени', default=False)
    objects = models.QuerySet

    def __str__(self):
        return f'{self.short_name} (chatId={self.chat_id})'

    class Meta:
        verbose_name = 'Сотрудники'
        verbose_name_plural = 'Сотрудники'


class MessageQuerySet(models.QuerySet):
    def delete(self):
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        for obj in self:
            try:
                bot.delete_message(chat_id=obj.telegram_employee.chat_id, message_id=obj.message_id)
            except TelegramError:
                bot.send_message(chat_id=obj.telegram_employee.chat_id,
                                 text=f'Не получилось удалить сообщение по заявке № {obj.request_number}. '
                                      f'Удалите его в ручную!')

        super(MessageQuerySet, self).delete()


class Message(models.Model):
    objects = MessageQuerySet.as_manager()
    telegram_employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message_id = models.CharField('Id сообщений телеграмм', max_length=15, null=True)
    request_number = models.IntegerField('Номер заявки в HelpDesk')

    def __str__(self):
        return f'Сообщение пользователя {self.telegram_employee.short_name} по заявке {self.request_number}'

    class Meta:
        verbose_name = 'Сообщения'
        verbose_name_plural = 'Сообщения'

    def delete(self, using=None, keep_parents=False):
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        try:
            bot.delete_message(chat_id=self.telegram_employee.chat_id, message_id=self.message_id)
        except TelegramError:
            bot.send_message(chat_id=self.telegram_employee.chat_id,
                             text=f'Не получилось удалить сообщение по заявке № {self.request_number}. '
                                  f'Удалите его в ручную!')

        super(Message, self).delete()

    @classmethod
    def send(cls, employee, request_number, text, reply_markup):
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
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
