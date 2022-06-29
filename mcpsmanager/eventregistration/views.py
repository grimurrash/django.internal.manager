from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from eventregistration.models import Event
from eventregistration.utils import RegistrationMethod, RegistrationError, NotFreeSeatsError, \
    OneUserRegistrationLimitError
from eventregistration.utils import NotEventLimitError, ParticipantDataSaveError, DateOfBirthParseError


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
def refresh_google_table(_, event_slug: str):
    event = Event.objects.get(slug=event_slug)
    count = RegistrationMethod.refresh_google_table(event=event)
    return JsonResponse({
        'status': True,
        'count': count
    })
