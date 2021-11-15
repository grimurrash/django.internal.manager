import base64
import gspread
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from teamsevent.funtions import get_client
from teamsevent.models import Group, TeamsEvent, Member


def file_convert(file: InMemoryUploadedFile) -> InMemoryUploadedFile:
    return file


@csrf_exempt
def create_microsoft_user(request: HttpRequest):
    event_name = request.POST.get('event')
    event = TeamsEvent.get_or_create(event_name=event_name)
    gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
    spreadsheet = gc.open_by_key('1m6cnFPkNFqP2M1M872b37t7CymDW_oW1CFSvQd-6JCo')
    sheets = spreadsheet.worksheets()
    print('sheets', sheets)
    client = get_client()
    for sheet in sheets:
        if sheet.title == 'все':
            continue
        rows = sheet.get_all_values()
        rows.pop(0)
        group = Group.get_or_create(name=sheet.title, event=event, microsoft_client=client)
        print('group', group)

        for index, row in enumerate(rows):
            if row[0] == '' or row[2] == '':
                continue
            member = Member.create(unique_id=row[0],
                                   surname=row[2],
                                   first_name=row[3],
                                   last_name=row[4],
                                   personal_email=row[6],
                                   group=group,
                                   microsoft_client=client)
            if member.personal_email != row[6]:
                print('Update personal email', member.email)
                member.personal_email = row[6]
                member.is_send_login_message = False
                member.save()

    return HttpResponse('Конец')


@csrf_exempt
def send_mails(request: HttpRequest):
    event_name = request.POST.get('event')
    events = TeamsEvent.objects.filter(name=event_name)
    if not events:
        return HttpResponse('Нет такого мероприятия')
    event = events.first()
    file = request.FILES.get('file')
    file_attachment = {
        '@odata.type': '#microsoft.graph.fileAttachment',
        'name': file.name,
        'contentType': file.content_type,
        'contentBytes': base64.b64encode(file.read()).decode('utf-8')
    }

    groups = Group.objects.filter(event=event)
    if not groups:
        return HttpResponse('Нет групп в данном мероприятие')

    client = get_client()
    send_email = request.POST.get('send_email')
    print('send count', Member.objects.filter(is_send_login_message=True).count())
    print('need send count', Member.objects.filter(is_send_login_message=False).count())

    #
    for group in groups:
        for member in group.member_set.filter(is_send_login_message=False):
            print('member...')
            result = member.send_login_details(file_attachment=file_attachment, microsoft_client=client,
                                               send_email=send_email)
            if not result:
                return HttpResponse('Ошибка')
    return HttpResponse('Конец')


def get_member(request: HttpRequest):
    members = Member.objects.filter(email=request.GET.get('email'))
    return_text = ''
    for member in members:
        return_text += f'email: {member.email}\ngroup: {member.group}\npersonal_email {member.personal_email}\n ' \
                       f'password: {member.password}\n\n'
    return HttpResponse(return_text)


@csrf_exempt
def send_mail(request: HttpRequest):
    file = request.FILES.get('file')
    file_attachment = {
        '@odata.type': '#microsoft.graph.fileAttachment',
        'name': file.name,
        'contentType': file.content_type,
        'contentBytes': base64.b64encode(file.read()).decode('utf-8')
    }

    client = get_client()
    send_email = request.POST.get('send_email')
    member = Member.objects.filter(personal_email=request.POST.get('personal_email'))
    if not member:
        return HttpResponse('ОШИБКА, ТАКОГО УЧАСТНИКА НЕТ')
    member = member.first()
    print('send mail...')
    result = member.send_login_details(file_attachment=file_attachment, microsoft_client=client,
                                       send_email=send_email)
    if not result:
        return HttpResponse('Ошибка')

    return HttpResponse('Конец')


def delete_microsoft_user(request: HttpRequest):
    event_name = request.GET.get('event')
    events = TeamsEvent.objects.filter(name=event_name)
    if not events:
        return HttpResponse('Нет такого мероприятия')
    event = events.first()
    groups = Group.objects.filter(event=event)
    if not groups:
        return HttpResponse('Нет групп в данном мероприятие')
    client = get_client()
    for group in groups:
        group.delete_microsoft_group(client)
    event.delete()
    return HttpResponse('Конец')
