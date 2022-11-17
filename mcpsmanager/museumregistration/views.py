from datetime import datetime

import gspread
import collections
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from museumregistration.models import RegistrationMember
from museumregistration.utils import GoogleDrive


def museum_registation_limit(_):
    registation_limit = RegistrationMember.registation_limit()
    family_statuses = dict(RegistrationMember.FamilyStatus.choices)
    age_groups = dict(RegistrationMember.AgeGroup.choices)
    directions = dict(RegistrationMember.Direction.choices)
    shift_dates = dict(RegistrationMember.Shift.choices)
    shifts = dict()
    shift_open_date = 5
    if datetime.now() > datetime(2022, 6, 13):
        shift_open_date = 9
    if datetime.now() > datetime(2022, 7, 11):
        shift_open_date = 13

    disabled_date = 0
    if datetime.now() > datetime(2022, 6, 27):
        disabled_date = 4
    if datetime.now() > datetime(2022, 7, 4):
        disabled_date = 5
    if datetime.now() > datetime(2022, 7, 11):
        disabled_date = 6
    if datetime.now() > datetime(2022, 7, 18):
        disabled_date = 7
    if datetime.now() > datetime(2022, 7, 25):
        disabled_date = 8
    if datetime.now() > datetime(2022, 8, 1):
        disabled_date = 9
    if datetime.now() > datetime(2022, 8, 8):
        disabled_date = 10
    if datetime.now() > datetime(2022, 8, 15):
        disabled_date = 11
    if datetime.now() > datetime(2022, 8, 22):
        disabled_date = 12

    for shift_key in shift_dates.keys():
        if shift_key >= shift_open_date:
            shifts.setdefault(shift_key, {
                'name': shift_dates[shift_key],
                'visible': False
            })
        elif shift_key <= disabled_date:
            continue
        else:
            shifts.setdefault(shift_key, {
                'name': shift_dates[shift_key],
                'visible': True
            })

    min_date = '2009-01-01'
    max_date = '2014-12-31'

    # Временно убрали семейный статус "без статуса"
    # family_statuses.pop(0)

    return JsonResponse({
        'limit': registation_limit,
        'familyStatuses': family_statuses,
        'ageGroups': age_groups,
        'directions': directions,
        'shifts': shifts,
        'minDate': min_date,
        'maxDate': max_date
    }, safe=False)


@csrf_exempt
def save_museum_registation_member(request: WSGIRequest):
    try:
        data = request.POST.dict()
        files = request.FILES.dict()

        surname = str(data['surname']).strip()
        first_name = str(data['firstname']).strip()
        last_name = str(data['lastname']).strip()
        date_of_birth = datetime.fromtimestamp(int(data['dateOfBirth']))

        member_registration_count = RegistrationMember.objects.filter(
            surname=surname,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth.strftime('%Y-%m-%d')
        ).count()
        if member_registration_count >= 2:
            return JsonResponse(
                {'status': False, 'message': 'Вы зарегистрировались на 2 смены. Более регистрация не возможна.'})

        registation_limit = RegistrationMember.registation_limit()
        if int(registation_limit[int(data['selectedShift'])][int(data['selectedDirection'])]
               [int(data['selectedAgeGroup'])]) <= 0:
            return JsonResponse({'status': False, 'message': 'В данной смене не осталось мест.'})

        google_drive = GoogleDrive(settings.GOOGLE_CREDENTIALS_FILE_PATH)
        member_folder_name = f'{surname} {first_name} {last_name} | ' + date_of_birth.strftime('%d.%m.%Y')
        # member_folder_id = google_drive.create_folder(name=member_folder_name,
        #                                               folder_id=settings.GOOGLE_MUSEUMREGISTRATION_DOCUMENTS_FOLDER_ID)
        shift = dict(RegistrationMember.Shift.choices)[int(data['selectedShift'])]
        age_group = dict(RegistrationMember.AgeGroup.choices)[int(data['selectedAgeGroup'])]
        direction = dict(RegistrationMember.Direction.choices)[int(data['selectedDirection'])]
        member_folder_id = f"/{shift}/{direction}/{age_group}/{member_folder_name}"

        if files.get('familyStatusFile'):
            google_drive.create_file(file=files.get('familyStatusFile'), file_name="Подтверждение статуса семьи",
                                     folder_id=member_folder_id)
        if files.get('passportFile'):
            google_drive.create_file(file=files.get('passportFile'), file_name="Паспорт", folder_id=member_folder_id)
        if files.get('birthCertificateFile'):
            google_drive.create_file(file=files.get('birthCertificateFile'), file_name="Свидетельство о рождении",
                                     folder_id=member_folder_id)
        if files.get('medicalPolicyFile'):
            google_drive.create_file(file=files.get('medicalPolicyFile'), file_name="Медицинский полис",
                                     folder_id=member_folder_id)
        if files.get('consentToTheStorageOfPersonalDataFile'):
            google_drive.create_file(file=files.get('consentToTheStorageOfPersonalDataFile'),
                                     file_name="Согласие на обработку персональных данных",
                                     folder_id=member_folder_id)
        if files.get('contractFile'):
            google_drive.create_file(file=files.get('contractFile'), file_name="Договор",
                                     folder_id=member_folder_id)
        if files.get('applicationOneFile'):
            google_drive.create_file(file=files.get('applicationOneFile'), file_name="Приложение 1",
                                     folder_id=member_folder_id)
        if files.get('applicationTwoFile'):
            google_drive.create_file(file=files.get('applicationTwoFile'), file_name="Приложение 2",
                                     folder_id=member_folder_id)
        if files.get('applicationThreeFile'):
            google_drive.create_file(file=files.get('applicationThreeFile'), file_name="Приложение 3",
                                     folder_id=member_folder_id)
        if files.get('applicationFourFile'):
            google_drive.create_file(file=files.get('applicationFourFile'), file_name="Приложение 4",
                                     folder_id=member_folder_id)
        if files.get('applicationFiveFile'):
            google_drive.create_file(file=files.get('applicationFiveFile'), file_name="Приложение 5",
                                     folder_id=member_folder_id)
        if files.get('applicationSixFile'):
            google_drive.create_file(file=files.get('applicationSixFile'), file_name="Приложение 6",
                                     folder_id=member_folder_id)

        registration_member = RegistrationMember(
            surname=surname,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
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
            documents_link=f'local: {member_folder_id}'
            # documents_link=f'https://drive.google.com/drive/folders/{member_folder_id}?usp=sharing',
        )
        registration_member.save()
        registration_member.save_to_google_table(spreadsheet_id=settings.GOOGLE_MUSEUMREGISTRATION_SPREADSHEET_ID)
        registration_member.send_email_notification()
        # shutil.rmtree(f'tmp/{member_folder_id}')
        return JsonResponse({'status': True})
    except Exception as exception:
        return JsonResponse({
            'status': False,
            'message': 'Приносим извинения ведутся технические работы.',
            'error': str(exception)
        })


def refresh_google_table(_):
    all_member = RegistrationMember.objects.filter(shift__gte=5).all()
    def next_available_row(worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list) + 1)

    gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key('152bP-qXWK0tbj4kn9bOqu29JNv5jH8XLc6Hn1KH24zY')
    sheet = spreadsheet.worksheet('Участники')
    rows = sheet.get_all_values()
    add_member = list()
    for member in all_member:
        member_list = [str(member.surname), str(member.first_name), str(member.last_name),
                       member.date_of_birth.strftime('%Y-%m-%d'),
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
    # next_row = next_available_row(sheet)
    # google_values = sheet.get_all_values()
    # print(google_values)
    # pass
