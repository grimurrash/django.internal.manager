from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from answerstoquestions.models import Question
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_question(request: WSGIRequest):
    data = request.POST.dict()

    question = Question(
        question=data['question'],
        yes_answer_name='1.',
        no_answer_name='2.'
    )
    question.save()

    return JsonResponse({
        'status': True,
        'id': question.id,
        'form': question.get_form_url(),
        'chart': question.get_chart_url()
    })


@csrf_exempt
def get_question(_, question_id: int):
    try:
        question = Question.objects.get(id=question_id)
        return JsonResponse({
            'status': True,
            'id': question_id,
            'question': question.question,
            'yes_answer': question.yes_answer,
            'no_answer': question.no_answer,
            'yes_answer_name': question.yes_answer_name,
            'no_answer_name': question.no_answer_name
        })
    except Exception as exception:
        return JsonResponse({
            'status': False,
            'message': 'Произошла ошибка, перезагрузите страницу и попробуйте ещё',
            'error': str(exception)
        })


@csrf_exempt
def update_question(request: WSGIRequest, question_id: int):
    try:
        question = Question.objects.get(id=question_id)
        data = request.POST.dict()
        print(request.POST)
        if data['answer'] == 'yes':
            question.add_yes_answer()
        elif data['answer'] == 'no':
            question.add_no_answer()
        else:
            return JsonResponse({
                'status': False,
                'message': 'Не выбран ответ'
            })

        return JsonResponse({
            'status': True
        })
    except Exception as exception:
        return JsonResponse({
            'status': False,
            'message': 'Произошла ошибка, перезагрузите страницу и попробуйте ещё',
            'error': str(exception)
        })
