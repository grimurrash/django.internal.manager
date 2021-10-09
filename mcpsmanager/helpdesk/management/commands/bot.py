from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.utils.request import Request
from helpdesk.functions import do_report, report_on_statistics, report_on_current_request, delete_message
from helpdesk.functions import accept_button, done_button


class Command(BaseCommand):
    help = "Телеграм-бот"

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0
        )
        bot = Bot(
            request=request,
            token=settings.TELEGRAM_BOT_TOKEN
        )
        print(bot.get_me())

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        updater.dispatcher.add_handler(CommandHandler('report', do_report))
        updater.dispatcher.add_handler(
            CallbackQueryHandler(report_on_current_request, pattern='report_on_current_request'))
        updater.dispatcher.add_handler(CallbackQueryHandler(report_on_statistics, pattern='report_on_statistics'))
        updater.dispatcher.add_handler(CallbackQueryHandler(delete_message, pattern='delete_message'))
        updater.dispatcher.add_handler(CallbackQueryHandler(accept_button, pattern='accept'))
        updater.dispatcher.add_handler(CallbackQueryHandler(done_button, pattern='done'))
        updater.start_polling()
        updater.idle()
        pass
