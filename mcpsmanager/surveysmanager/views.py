from surveysmanager.models import Survey, SurveyAnswer
from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse


@csrf_exempt
def get_info(_, url: str):
    try:
        survey = Survey.objects.get(url=url)

        return JsonResponse({
            'status': True,
            'info': survey.get_info()
        })
    except Exception as exception:
        return JsonResponse({
            'status': False,
            'message': '',
            'error': f"{type(exception)}: {exception}"
        })


@csrf_exempt
def save_result(request: WSGIRequest, url: str):
    data = request.POST.dict()
    try:
        survey = Survey.objects.get(url=url)
        SurveyAnswer.create(survey, data)

        return JsonResponse({
            'status': True,
            'message': 'Вы успешно зарегистрировались!'
        })
    except Exception as exception:
        return JsonResponse({
            'status': False,
            'message': '',
            'error': f"{type(exception)}: {exception}"
        })


