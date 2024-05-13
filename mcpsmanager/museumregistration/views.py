from datetime import datetime

import gspread
import collections
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from museumregistration.models import RegistrationMember
from museumregistration.utils import FTPDrive
from transliterate import translit
import requests
import json

def registration_limit(_):
    registration_limit = RegistrationMember.registration_limit()
    family_statuses = dict(RegistrationMember.FamilyStatus.choices)
    age_groups = dict(RegistrationMember.AgeGroup.choices)
    directions = dict(RegistrationMember.Direction.choices)
    shift_dates = dict(RegistrationMember.Shift.choices)
    shifts = dict()
    shift_open_date = RegistrationMember.Shift.get_open_shift()

    disabled_date = RegistrationMember.Shift.get_disabled_shift()

    print(shift_open_date, disabled_date)
    for shift_key in shift_dates.keys():
        if shift_key >= shift_open_date:
            shifts.setdefault(shift_key, {
                'name': shift_dates[shift_key],
                'visible': False
            })
        elif shift_key < disabled_date:
            continue
        else:
            shifts.setdefault(shift_key, {
                'name': shift_dates[shift_key],
                'visible': True
            })

    # Временно убрали семейный статус "без статуса"
    family_statuses.pop(0)

    return JsonResponse({
        'limit': registration_limit,
        'familyStatuses': family_statuses,
        'ageGroups': age_groups,
        'directions': directions,
        'shifts': shifts,
    }, safe=False)


@csrf_exempt
def save_registration_member(request: WSGIRequest):
    try:
        data = request.POST.dict()
        files = request.FILES.dict()

        firstname = str(data['surname']).strip()
        surname = str(data['firstname']).strip()
        last_name = str(data['lastname']).strip()
        age = int(data['age'])

        member_registration_count = RegistrationMember.objects.filter(
            surname=firstname,
            first_name=surname,
            last_name=last_name,
            age=age
        ).count()
        if member_registration_count >= 2:
            return JsonResponse(
                {'status': False,
                 'message': 'Вы зарегистрировались на 2 смены. Вы зарегистрировались на 2 смены. Более регистрация не возможна.'})

        registration_limits = RegistrationMember.registration_limit()
        if int(registration_limits[int(data['selectedShift'])][int(data['selectedDirection'])]
               [int(data['selectedAgeGroup'])]) <= 0:
            return JsonResponse({'status': False, 'message': 'В данной смене не осталось мест.'})

        shift = dict(RegistrationMember.Shift.choices)[int(data['selectedShift'])]
        age_group = dict(RegistrationMember.AgeGroup.choices)[int(data['selectedAgeGroup'])]
        direction = dict(RegistrationMember.Direction.choices)[int(data['selectedDirection'])]

        member_folder_name = f'{surname} {firstname} {last_name} {age} лет'
        member_folder_path = translit(f"{shift}/{direction}/{age_group}/{member_folder_name}", language_code='ru', reversed=True)

        ftp_drive = FTPDrive(member_folder_path)

        if files.get('familyStatusFile'):
            ftp_drive.create_file(file=files.get('familyStatusFile'), file_name="Family Status Confirmation")
        if files.get('passportFile'):
            ftp_drive.create_file(file=files.get('passportFile'), file_name="Passport")
        if files.get('birthCertificateFile'):
            ftp_drive.create_file(file=files.get('birthCertificateFile'), file_name="Birth certificate")
        if files.get('medicalPolicyFile'):
            ftp_drive.create_file(file=files.get('medicalPolicyFile'), file_name="Medical policy")
        if files.get('contractFile'):
            ftp_drive.create_file(file=files.get('contractFile'), file_name="Contract")

        registration_member = RegistrationMember(
            surname=firstname,
            first_name=surname,
            last_name=last_name,
            age=age,
            phone_number=data['phoneNumber'],
            email=data['email'],
            actual_address=data['address'],
            school=data['school'],
            parent_fullname=data['parentFullName'],
            reserve_phone_number=data['reservePhoneNumber'],
            family_status=int(data['selectedFamilyStatus']),
            direction=int(data['selectedDirection']),
            age_group=int(data['selectedAgeGroup']),
            shift=int(data['selectedShift']),
            documents_link=f'fpt: {member_folder_path}'
        )
        registration_member.save()
        registration_member.save_to_google_table()
        return JsonResponse({'status': True})
    except Exception as exception:
        return JsonResponse({
            'status': False,
            'message': 'Приносим извинения, ведутся технические работы.',
            'error': str(exception)
        })


def refresh_google_table(_):
    all_member = RegistrationMember.objects.filter(shift__gte=5).all()

    def next_available_row(worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list) + 1)

    gc = gspread.service_account(settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key(settings.GOOGLE_MUSEUMREGISTRATION_SPREADSHEET_ID)
    sheet = spreadsheet.worksheet('Участники 2023')
    rows = sheet.get_all_values()
    add_member = list()
    for member in all_member:
        member_list = [str(member.surname), str(member.first_name), str(member.last_name),
                       str(member.age),
                       str(member.actual_address), str(member.school),
                       str(member.parent_fullname), str(member.phone_number), str(member.reserve_phone_number),
                       str(member.email),
                       str(member.get_family_status()), str(member.get_direction()),
                       str(member.get_age_group()), str(member.get_shift()), str(member.documents_link)]
        is_add = True
        for row in rows:
            row = row[0:15]
            row[3] = row[3][0:10]
            if collections.Counter(member_list) == collections.Counter(row[0:15]):
                is_add = False
                break
        if is_add:
            add_member.append(member_list)

    next_row = next_available_row(sheet)
    sheet.update(f'A{next_row}', add_member)
    return JsonResponse({
        'add_member_count': len(add_member),
        'all_member': len(all_member),
        'add_member': add_member,
    })

