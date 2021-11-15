import json
from django.db import models
from msgraph.core import GraphClient
from teamsevent.funtions import transliterate


class TeamsEvent(models.Model):
    name = models.CharField('Наименование мероприятия', max_length=255)
    objects = models.QuerySet.as_manager()

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['-id']

    def __str__(self):
        return f'TeamsEvent: {self.name}'

    @classmethod
    def get_or_create(cls, event_name: str):
        events = TeamsEvent.objects.filter(name=event_name)
        print('event', events)
        if not events:
            event = TeamsEvent(name=event_name)
            event.save()
        else:
            event = events.first()
        return event


class Group(models.Model):
    microsoft_id = models.CharField('Id в Microsoft', max_length=255)
    name = models.CharField('Наименование группы', max_length=255)
    event = models.ForeignKey(TeamsEvent, on_delete=models.CASCADE)
    objects = models.QuerySet.as_manager()

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['-id']

    def __str__(self):
        return f'MicrosoftGroup: {self.name}'

    @classmethod
    def create(cls, display_name: str, mail_nickname: str, event: TeamsEvent, microsoft_client: GraphClient):
        group_data = {
            "displayName": display_name,
            "mailEnabled": False,
            "mailNickname": mail_nickname,
            "securityEnabled": True
        }
        microsoft_group = microsoft_client.post(url='/groups',
                                                data=json.dumps(group_data),
                                                headers={'Content-Type': 'application/json'})
        group = cls(name=display_name, event=event, microsoft_id=dict(microsoft_group.json()).get('id'))
        group_licenses = microsoft_client.post(
            url=f'/groups/{group.microsoft_id}/assignLicense',
            data=json.dumps({
                "addLicenses": [
                    {
                        "disabledPlans": ["94763226-9b3c-4e75-a931-5c89701abe66"],
                        "skuId": "guid"
                    }
                ],
                "removeLicenses": []
            }),
            headers={'Content-Type': 'application/json'})
        print('Create group', display_name, microsoft_group.status_code, group_licenses.status_code)
        group.save()
        return group

    @classmethod
    def get_or_create(cls, name: str, event: TeamsEvent, microsoft_client: GraphClient):
        group_name = f'TeamsGroup: {name.title()}'
        groups = cls.objects.filter(name=group_name, event=event)
        if not groups:
            group = cls.create(display_name=group_name,
                               mail_nickname=transliterate(f'teams_group_{name}'),
                               event=event,
                               microsoft_client=microsoft_client)
        else:
            group = groups.first()
        return group

    def delete_microsoft_group(self, microsoft_client: GraphClient):
        print('Delete group start', self.name)
        for member in self.member_set.all():
            member.delete_member(microsoft_client=microsoft_client)
        group_licenses = microsoft_client.post(
            url=f'/groups/{self.microsoft_id}/assignLicense',
            data=json.dumps({
                "addLicenses": [],
                "removeLicenses": ["94763226-9b3c-4e75-a931-5c89701abe66"]
            }),
            headers={'Content-Type': 'application/json'})
        group_delete = microsoft_client.delete(url=f'/groups/{self.microsoft_id}')
        print('Delete group end', self.name, group_licenses.status_code, group_delete.status_code)
        self.delete()
        return


class Member(models.Model):
    microsoft_id = models.CharField('ID в microsoft', max_length=255)
    email = models.CharField('email', max_length=255)
    password = models.CharField('password', max_length=255)
    personal_email = models.CharField('Личная почта', max_length=255)
    is_send_login_message = models.BooleanField('Отправлено ли письмо с данным по авторизации', default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    objects = models.QuerySet.as_manager()

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        ordering = ['-id']

    def __str__(self):
        return f'MicrosoftUser: {self.email}'

    def send_login_details(self, file_attachment: dict, send_email: str, microsoft_client: GraphClient):
        main_room_url = 'https://teams.microsoft.com/l/team/19%3aWTg8Rb-_xNlt40aIoEanxpoPmYkYfPfMRCNtfrivrws1%40thread.tacv2/conversations?groupId=4887358c-54ff-4673-b28d-bd4af7c98983&tenantId=6f3cdfd7-3023-47a8-90d9-249d30a52f8f'
        body = {
            "message": {
                "subject": "Онлайн-школа волонтеров «Добровольчество» - Второй день.",
                "body": {
                    "contentType": "HTML",
                    "content": f"""
                    <p><b>Добро пожаловать в онлайн-школу волонтеров «Добровольчество»!</b></p>
                    
                    <p>11 ноября стартует второй день онлайн-школы.</p>
                    
                    <p>Мы рады видеть Вас в числе участников онлайн-школы волонтеров города Москвы.</p>
                    
                    <p>В этом письме Вы найдете инструкцию, которая поможет Вам получить доступ к Teams под 
                    уникальной учетной записью. Внутри рабочего кабинета Teams вы найдете доступ к двум кабинетам - 
                    общему лекционному и отрядному. Во время проведения школы, спикер будет приглашать Вас в один из 
                    этих кабинетов. </p>
                    <p>Познакомиться с программой Школы волонтеров «Добровольчество» вы можете на сайте 
                    https://patriotsport.moscow/patriotizm/volontery/dobrovolchestvo/</p>
                    <hr>
                    <p><b>Второй день мероприятия начинается 11 ноября в 14:30 в общей комнате Teams.</b><br>
                    <a href="{main_room_url}"> Ссылка для входа в общую комнату Teams </a></p>
                    <p><i>Вход в комнату возможен только по учетной записи, указанной ниже.</i></p>
                    <p><b>Данные для входа</b><br>
                    <b>Почта Microsoft:</b> {self.email}<br>
                    <b>Пароль:</b> {self.password}</p>
                    <hr>
                    
                    <p><b>До встречи!</b><br>
                    Подписывайтесь на телеграмм канал Волонтерского движения! 
                    <a href="https://t.me/joinchat/ZQmuO7lkfhdkYWRi">Подписаться</a>
                    </p><br>
                    
                    <p><b><i>С уважением,<br>команда Московского центра<br> «Патриот.Спорт»</p><br>
                    
                    <p><b>В случае  возникновения проблем со входом, пишите ответным письмом</b></p>
                    """
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": self.personal_email
                        }
                    }
                ],
                "attachments": [
                    file_attachment
                ]
            },
            "saveToSentItems": "true"
        }
        result = microsoft_client.post(url=f'/users/{send_email}/sendMail',
                                       data=json.dumps(body),
                                       headers={'Content-Type': 'application/json'})
        print('send mail user:', self.email, 'to', self.personal_email, 'status', result.status_code)
        if result.status_code != 202:
            print('result', result.json())
            return False
        self.is_send_login_message = True
        self.save()
        return True

    def delete_member(self, microsoft_client: GraphClient):
        user_delete = microsoft_client.delete(url=f'/users/{self.microsoft_id}')
        print('Delete member', self.email, user_delete.status_code)
        self.delete()
        return

    @classmethod
    def create(cls,
               unique_id: int,
               surname: str,
               first_name: str,
               last_name: str,
               personal_email: str,
               group: Group,
               microsoft_client: GraphClient):
        surname = surname.strip()
        surname_t = transliterate(surname.replace("ь", ""))
        first_name = first_name.strip()
        last_name = last_name.strip()
        display_name = f'{surname} {first_name} {last_name}'.strip()
        mailNickname = f'user{unique_id}.{surname_t}{transliterate(first_name[0]).upper()}'
        if last_name != '':
            mailNickname += transliterate(last_name[0]).upper()
        email = mailNickname + '@cpvs.moscow'
        user = cls.objects.filter(email=email)
        if user:
            return user.first()

        password = f'pass{unique_id}!{transliterate(surname[0]).lower()}{surname_t.upper()}'
        user_data = {
            'accountEnabled': 'true',
            'displayName': display_name,
            'mailNickname': mailNickname,
            'userPrincipalName': email,
            "surname": surname,
            "givenName": first_name,
            "usageLocation": "RU",
            "identities": [
                {
                    "signInType": "userPrincipalName",
                    "issuer": "voenpatriot.onmicrosoft.com",
                    "issuerAssignedId": email
                }
            ],
            "passwordProfile": {
                "forceChangePasswordNextSignIn": 'false',
                "password": password
            },
            "passwordPolicies": "DisablePasswordExpiration"
        }
        print('Create user:', user_data)
        microsoft_user = microsoft_client.post(url='/users',
                                               data=json.dumps(user_data),
                                               headers={'Content-Type': 'application/json'})
        if microsoft_user.status_code != 201:
            print('microsoft_user', microsoft_user.status_code, microsoft_user.json())
        user = cls(email=email, password=password, personal_email=personal_email, group=group,
                   microsoft_id=dict(microsoft_user.json()).get('id'))
        user.save()

        result = microsoft_client.post(url=f'/groups/{group.microsoft_id}/members/$ref',
                                       data=json.dumps({
                                           '@odata.id': f'https://graph.microsoft.com/v1.0/users/{user.microsoft_id}'
                                       }),
                                       headers={'Content-Type': 'application/json'})
        print('update group member', result.status_code)

        return user
