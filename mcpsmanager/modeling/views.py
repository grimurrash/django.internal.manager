import uuid
from modeling.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.handlers.wsgi import WSGIRequest
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path


def get_models(_):
    ship_models = ShipModel.objects.exclude(main_photo__isnull=True) \
        .filter(status=ShipModel.ShopModelStatus.Received) \
        .to_list()

    return JsonResponse(ship_models, safe=False)


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

        file_dir = uuid.uuid1()

        photos = []
        for key, file in files.items():
            if key == 'passport_file':
                password_path = f'uploads/ship-modeling/{file_dir}/passport{Path(file.name).suffix}'
                default_storage.save(password_path, ContentFile(file.read()))
            elif key == 'drawing_file':
                drawing_path = f'uploads/ship-modeling/{file_dir}/drawing{Path(file.name).suffix}'
                default_storage.save(drawing_path, ContentFile(file.read()))
            else:
                photos_path = f'uploads/ship-modeling/{file_dir}/{key}{Path(file.name).suffix}'
                photos.append(photos_path)
                default_storage.save(photos_path, ContentFile(file.read()))

        ship_type = None
        if data.get('type'):
            ship_type = ShipType.objects.get(id=int(data.pop('type')))

        model = ShipModel(
            model_name=model_data.get('name'),
            model_type=ship_type,
            model_scale=model_data.get('scale'),
            surname=model_data.get('surname'),
            first_name=model_data.get('firstName'),
            last_name=model_data.get('lastName'),
            date_of_birth=date_of_birth,
            educational_organization=model_data.get('eduOrg'),
            email=model_data.get('email'),
            phone_number=model_data.get('phone'),
            description=model_data.get('description'),
            zip_code=model_data.get('zipCode'),
            city_country=model_data.get('cityCountry'),
            actual_address=model_data.get('address'),
            model_passport=password_path,
            model_drawing=drawing_path,
            main_photo=None,
            model_photos=json.dumps(photos),
        )
        model.save()
        return JsonResponse({
            'status': True,
            'id': model.id
        })

    except Exception as error:
        return JsonResponse({
            'status': False,
            'message': 'Не удалось создать заявку на участие, попробуйте позже!'
        })
