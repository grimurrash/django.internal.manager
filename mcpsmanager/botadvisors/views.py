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
    except Interview.DoesNotExist as error:
        bot.send_message(text=f'{str(error)} {json_body}', chat_id=332158440)
        update = Update.de_json(json_body, bot)
        chat_id = 0
        if update.message:
            chat_id = update.message.chat.id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat.id

        if chat_id != 0:
            user_interview, created = Interview.objects.get_or_create({}, chat_id=chat_id)
            interview_step(user_interview, bot, update)
        return JsonResponse({
            'status': False,
            'error': error,
            'json_body': json_body
        })
    except Exception as error:
        return JsonResponse({
            'status': False,
            'error': error,
            'json_body': json_body
        })
        bot.send_message(text=f'{str(error)} {json_body}', chat_id=332158440)
        pass

    return JsonResponse({
        'status': True,
        'json_body': json_body
    })


def refresh_test_results(_):
    result = Interview.update_goggle_table()
    return JsonResponse({
        'status': True,
        'result': result,
    })


def send_finish_message(_):
    rows = Interview.send_finish_message()
    return JsonResponse({
        'status': True,
        'count': len(rows),
        'rows': rows
    })

def send_result_message(_):
    rows = Interview.send_result_message()
    return JsonResponse({
        'status': True,
        'count': len(rows),
        'rows': rows
    })

def refresh_questions(_):
    Questions.refresh()
    return JsonResponse({
        'status': True,
    })
