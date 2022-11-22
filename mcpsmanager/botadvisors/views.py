from botadvisors.models import *
from botadvisors.methods import *
from django.http import JsonResponse, HttpResponse
from telegram import Bot, Update
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def bot_webhook(request: WSGIRequest):
    bot = Bot(token=settings.ADVISORS_BOT_TOKE)
    json_body = json.loads(request.body)
    try:
        update = Update.de_json(json_body, bot)
        if update.message:
            chat_id = update.message.chat.id

            user_interview, created = Interview.objects.get_or_create({}, chat_id=chat_id)
            interview_step(user_interview, bot, update)
    except Interview.DoesNotExist:
        update = Update.de_json(json_body, bot)
        chat_id = 0
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id

        if chat_id != 0:
            user_interview, created = Interview.objects.get_or_create({}, chat_id=chat_id)
            interview_step(user_interview, bot, update)
    except Exception as error:
        pass
        # bot.send_message(text=f'{str(error)} {json_body}', chat_id=332158440)
        # raise error

    return HttpResponse(True)


def start_test(request: WSGIRequest):
    bot = Bot(token=settings.ADVISORS_BOT_TOKE)
    json_body = json.loads(request.body)
    update = Update.de_json(json_body, bot)
    chat_id = '332158440'
    user_interview, created = Interview.objects.get_or_create({}, chat_id=chat_id)
    interview_step(user_interview, bot, update)
    return JsonResponse({
        'status': True,
    })


def refresh_questions(_):
    Questions.refresh()
    return JsonResponse({
        'status': True,
    })
