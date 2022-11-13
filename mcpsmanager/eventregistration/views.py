from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from eventregistration.utils import RegistrationMethod, RegistrationError, NotFreeSeatsError, \
    OneUserRegistrationLimitError
from eventregistration.utils import NotEventLimitError, ParticipantDataSaveError, DateOfBirthParseError
from eventregistration.models import *


@csrf_exempt
def get_event_info(_, event_slug: str):
    try:
        event = Event.objects.get(slug=event_slug)

        return JsonResponse({
            'status': True,
            'event': event.get_full_info()
        })
    except Exception as exception:
        return JsonResponse({
            'status': False,
            'message': '',
            'error': f"{type(exception)}: {exception}"
        })


@csrf_exempt
def save_registration(request: WSGIRequest, event_slug: str):
    data = request.POST.dict()
    files = request.FILES.dict()
    try:
        event = Event.objects.get(slug=event_slug)

        RegistrationMethod.registration(event=event, data=data, files=files)

        return JsonResponse({
            'status': True,
            'message': 'Вы успешно зарегистрировались!'
        })
    except OneUserRegistrationLimitError as error:
        return JsonResponse({
            'status': False,
            'message': error.message,
            'error': str(error)
        })
    except Event.DoesNotExist as error:
        return JsonResponse({
            'status': False,
            'message': "Мероприятие не существует!",
            'error': f"{type(error)} | {error}"
        })
    except (NotFreeSeatsError, NotEventLimitError) as error:
        return JsonResponse({
            'status': False,
            'message': "Отсутствуют свободные места!",
            'error': str(error)
        })
    except ParticipantDataSaveError as error:
        return JsonResponse({
            'status': False,
            'message': "Отсутствуют обязательные поля!",
            'error': str(error)
        })
    except DateOfBirthParseError as error:
        return JsonResponse({
            'status': False,
            'message': error.message,
            'error': str(error)
        })
    except RegistrationError as error:
        return JsonResponse({
            'status': False,
            'message': 'Ошибка регистрации. '
                       'Техподдержка уже исправляет проблему. '
                       'Просьба попробывать снова через несколько часов',
            'error': str(error)
        })


@csrf_exempt
def create_group(request: WSGIRequest, event_slug: str):
    event = Event.objects.get(slug=event_slug)
    if event_slug == 'avangard-transfer':
        for number in range(40):
            number = number + 1
            shift = Shift(name=f"Группа {number}", event=event)
            limit = EventLimit(event=event, shift=shift, limit=30, free_seats=30)
            shift.save()
            limit.save()

        for number in range(24):
            number = number + 1
            direction = Direction(name=f"Автобус №{number}", event=event)
            limit = EventLimit(event=event, direction=direction, limit=50, free_seats=50)
            direction.save()
            limit.save()
    return JsonResponse({
        'status': True,
    })


@csrf_exempt
def refresh_google_table(_, event_slug: str):
    event = Event.objects.get(slug=event_slug)
    count = RegistrationMethod.refresh_google_table(event=event)
    return JsonResponse({
        'status': True,
        'count': count
    })
