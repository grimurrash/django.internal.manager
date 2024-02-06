from modeling.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from datetime import datetime
from django.core.files.base import ContentFile
from pathlib import Path
import requests
import hashlib
import hmac
import json

def get_models(_):
    ship_models = ShipModel.objects.exclude(main_photo__isnull=True) \
        .filter(status=ShipModel.ShopModelStatus.Received) \
        .to_list()
    ship_models_count = ShipModel.objects.count()

    return JsonResponse({
        'models': ship_models,
        'total_count': ship_models_count
    }, safe=False)


def get_model_types(_):
    ship_model_types = ShipType.objects.to_list()

    return JsonResponse(ship_model_types, safe=False)

def get_model_info(_, model_id: int):
    model_info = ShipModel.objects.get(id=model_id).to_dict()

    return JsonResponse(model_info, safe=False)


@csrf_exempt
def add_model(request: WSGIRequest):
    data: dict = request.POST.dict()
    files = request.FILES.dict()
    try:
        model_data = data.copy()
        date_of_birth = datetime.fromtimestamp(int(data.pop('dateOrBirth')))
        model_data['dateOfBirth'] = date_of_birth.strftime('%d-%m-%Y')

        ship_type = None
        if data.get('type'):
            ship_type = ShipType.objects.get(id=int(data.pop('type')))
        model = ShipModel(
            model_name=model_data.get('name'),
            model_type=ship_type,
            model_scale=model_data.get('scale'),
            surname=model_data.get('surname'),
            first_name=model_data.get('firstName'),
            last_name=model_data.get('lastName', ''),
            date_of_birth=date_of_birth,
            educational_organization=model_data.get('eduOrg'),
            email=model_data.get('email'),
            phone_number=model_data.get('phone'),
            description=model_data.get('description'),
            zip_code=model_data.get('zipCode'),
            city_country=model_data.get('cityCountry'),
            actual_address=model_data.get('address'),
        )
        photos = []
        for key, file in files.items():
            if key == 'passport_file':
                model.model_passport.save(f'passport{Path(file.name).suffix}', ContentFile(file.read()))
            elif key == 'drawing_file':
                model.model_drawing.save(f'drawing{Path(file.name).suffix}', ContentFile(file.read()))
            else:
                photos.append({
                    'name': f'{key}{Path(file.name).suffix}',
                    'file': file
                })
        model.save()
        for item in photos:
            shop_model_file = ShipModelFile(ship_model_id=model)
            shop_model_file.file.save(item.get('name'), ContentFile(item.get('file').read()))
            shop_model_file.save()
        return JsonResponse({
            'status': True,
            'id': model.id
        })

    except Exception as error:
        return JsonResponse({
            'status': False,
            'message': 'Не удалось создать заявку на участие, попробуйте позже!'
        })
