import json

import gspread
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.csrf import csrf_exempt

from videorating.models import *
from django.http import JsonResponse


def import_participant(_):
    gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key('1Gzn-7g_X903VCWyoa2U9l8vj1infiiIEzKSV9s2HFAs')
    worksheets = list(spreadsheet.worksheets())

    for worksheet in worksheets:
        rows = worksheet.get_all_values()
        for row in rows:
            if row[2] == 'Наименование школы' or row[2] == '':
                continue
            part = Participant(
                type=worksheet.title,
                school=row[2],
                team_name=row[5],
                video_url=row[8],
                leader_fio=row[11] if len(row) > 11 else None,
                reference_url=row[12] if len(row) > 12 else None,
            )
            part.save()
    return JsonResponse({'status': True})


def get_list(request: WSGIRequest):
    user = request.GET.dict().get('user')
    participant_type = request.GET.dict().get('type')
    participants = Participant.objects.filter(type=participant_type).all()

    evaluations = Evaluation.objects.all()

    participant_list = []
    for participant in participants:
        participant_evaluations = evaluations.filter(participant=participant)
        there_rating = participant_evaluations.filter(appraiser=user).first()
        participant_list.append(participant.to_dict(participant_evaluations, there_rating.points if there_rating is not None else None))

    return JsonResponse({'items': participant_list})


@csrf_exempt
def add_evaluation(request: WSGIRequest):
    post_data = request.POST.dict()
    participant = post_data.get('participant')
    points = post_data.get('points')
    comment = post_data.get('comment')
    user = post_data.get('user')

    evaluation = Evaluation(
        points=points,
        appraiser=user,
        comment=comment if comment is not None else None,
        participant_id=participant
    )
    evaluation.save()
    return JsonResponse({'status': True, 'id': evaluation.id})
