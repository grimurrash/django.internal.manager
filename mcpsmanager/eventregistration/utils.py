from eventregistration.models import *
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path
import urllib.parse
import json


class RegistrationError(Exception):
    message: str = "Ошибка регистрации"
    error_message: str = ""

    def __init__(self, error_message=""):
        self.error_message = error_message

    def __str__(self):
        return_message = f"{type(self)} {self.message}"
        if self.error_message != "":
            return_message += f" | {self.error_message}"
        return return_message


class SendRegistrationMailNotificationError(RegistrationError):
    message = "Ошибка отправки уведомления о регистрации"


class NotEventLimitError(RegistrationError):
    message = "Отсутствуют свободные места"


class NotFreeSeatsError(RegistrationError):
    message = "Отсутствуют свободные места"


class ParticipantDataSaveError(RegistrationError):
    message = "Ошибка при сохранении данных"


class DateOfBirthParseError(RegistrationError):
    message = "Неверный формат даты рождения"


class OneUserRegistrationLimitError(RegistrationError):
    message = "Достигнуто максимальное количество возможных регистраций"


class RegistrationMethod:
    @classmethod
    def registration(cls, event: Event, data: dict, files: dict):
        # TODO Добавить валидацию

        return getattr(cls, data.get('registration_method', 'default'))(event=event, data=data, files=files)

    @classmethod
    def default(cls, event: Event, data: dict, files: dict):
        try:
            participant_data = data.copy()
            surname = data.pop('surname')
            first_name = data.pop('first_name')
            last_name = data.pop('last_name')
            email = data.pop('email')
            date_of_birth = datetime.fromtimestamp(int(data.pop('date_of_birth')))
            participant_data['date_of_birth'] = date_of_birth.strftime('%d-%m-%Y')

            shift = None
            age_group = None
            direction = None

            if data.get('shift_id'):
                shift = Shift.objects.get(id=int(data.pop('shift_id')))
                participant_data.setdefault('shift', str(shift))
            if data.get('age_group_id'):
                age_group = AgeGroup.objects.get(id=int(data.pop('age_group_id')))
                participant_data.setdefault('age_group', str(age_group))
            if data.get('direction_id'):
                direction = Direction.objects.get(id=int(data.pop('direction_id')))
                participant_data.setdefault('direction', str(direction))

            check_limit = EventLimit.objects.get(
                event=event,
                shift=shift,
                age_group=age_group,
                direction=direction
            )

            if check_limit.free_seats <= 0:
                raise NotFreeSeatsError()

            existence_participant_count = Participant.objects.filter(
                surname=surname,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                event=event
            ).count()

            if existence_participant_count >= event.limit_for_one_user:
                raise OneUserRegistrationLimitError()

            if existence_participant_count > 0:
                is_register_from_shift = Participant.objects.filter(
                    surname=surname,
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth,
                    shift=shift,
                    age_group=age_group,
                    direction=direction,
                    event=event
                ).count()
                if is_register_from_shift > 0:
                    raise OneUserRegistrationLimitError()

            participant_files_dir = None
            if len(files) > 0:
                participant_files_dir = event.slug
                if shift:
                    participant_files_dir += '/' + shift.name
                if direction:
                    participant_files_dir += '/' + direction.name
                if age_group:
                    participant_files_dir += '/' + age_group.name

                participant_files_dir += f'/{surname} {first_name} {last_name} | ' + date_of_birth.strftime('%d.%m.%Y')
                for key, file in files.items():
                    try:
                        document = Documents.objects.get(id=int(str(key).replace('upload_file_', '')))
                        filename = document.name + Path(file.name).suffix
                    except:
                        filename = file.name

                    default_storage.save(f'uploads/events/{participant_files_dir}/{filename}', ContentFile(file.read()))

            participant = Participant(
                surname=surname,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                email=email,
                additionally_data=json.dumps(data),
                event=event,
                shift=shift,
                age_group=age_group,
                direction=direction,
                files_dir=participant_files_dir,
            )
            participant.save()
            check_limit.free_seats -= 1
            check_limit.save()

            if event.is_save_google_table:
                save_data = [
                    participant.id,
                    surname,
                    first_name,
                    last_name,
                    date_of_birth.strftime('%d-%m-%Y'),
                    email,
                ]
                try:
                    for key, value in data.items():
                        save_data.append(str(value))

                    if shift:
                        save_data.append(str(shift))
                    if age_group:
                        save_data.append(str(age_group))
                    if direction:
                        save_data.append(str(direction))

                    if participant_files_dir:
                        save_data.append(str(participant_files_dir))

                    event.save_google_table(
                        data=save_data,
                        table_name=check_limit.get_name()
                    )
                except Event.SaveDataToGoogleTableError as error:
                    if event.support_email_address:
                        report_message = ''
                        for value in save_data:
                            report_message += f'<p>{value}</p>'
                        event.send_support(
                            subject="Не удалось добавить в гугл таблицу информацию о регистрации!",
                            message=f"<p>Ошибка: {str(error)}</p>\n" + report_message
                        )

            if event.is_send_registration_mail_notification:
                participant_data.setdefault('event', str(event))
                is_send = MailNotification.send_registration_mail_notification(
                    event=event,
                    email=email,
                    data=participant_data
                )
                if is_send:
                    participant.is_send_registration_mail = True
                    participant.save()
        except OneUserRegistrationLimitError as error:
            raise error
        except NotFreeSeatsError as error:
            raise error
        except OverflowError as error:
            raise DateOfBirthParseError(str(error))
        except EventLimit.DoesNotExist as error:
            raise NotEventLimitError(str(error))
        except (ValueError, KeyError) as error:
            raise ParticipantDataSaveError(str(error))
        except Exception as exception:
            raise RegistrationError(str(exception))

    @classmethod
    def refresh_google_table(cls, event: Event):
        if event.is_save_google_table:
            all_participant = Participant.objects.filter(event=event)
            all_save_data = dict()
            for participant in all_participant:
                save_data = [
                    participant.id,
                    participant.surname,
                    participant.first_name,
                    participant.last_name,
                    participant.date_of_birth.strftime('%d-%m-%Y'),
                    participant.email,
                ]
                if participant.additionally_data:
                    data = json.loads(participant.additionally_data)
                    for key, value in data.items():
                        save_data.append(str(value))

                if participant.shift:
                    save_data.append(str(participant.shift))
                if participant.age_group:
                    save_data.append(str(participant.age_group))
                if participant.direction:
                    save_data.append(str(participant.direction))

                if participant.files_dir:
                    save_data.append(str(participant.files_dir))
                try:
                    limit = EventLimit.objects.get(
                        event=event,
                        shift=participant.shift,
                        age_group=participant.age_group,
                        direction=participant.direction
                    )
                except Exception as ex:
                    continue

                if all_save_data.get(limit.get_name()):
                    all_save_data[limit.get_name()].append(save_data)
                else:
                    all_save_data.setdefault(limit.get_name(), [save_data])

            if not event.is_save_google_table or not event.google_spreadsheet_id:
                return

            gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_FILE_PATH)
            spreadsheet = gc.open_by_key(str(event.google_spreadsheet_id))
            worksheets = list(spreadsheet.worksheets())

            for table_name, save_data in all_save_data.items():
                is_exist_sheet = False
                for worksheet in worksheets:
                    if worksheet.title == table_name:
                        is_exist_sheet = True
                        break

                if is_exist_sheet:
                    continue
                else:
                    sheet = spreadsheet.add_worksheet(table_name, len(save_data) + 1, len(save_data[0]) + 1)
                    worksheets.append(sheet)

                sheet.update(f'A1', save_data)
            return len(all_participant)


class MailNotification:
    @classmethod
    def send_registration_mail_notification(cls, event: Event, email: str, data: dict):
        try:
            message = str(event.registration_mail_text).format(**data)
            send_result = MicrosoftGraph.send_mail(
                from_address=str(event.from_email_address),
                to_address=email,
                message=message,
                subject=str(event.registration_mail_subject)
            )
            if not send_result:
                raise SendRegistrationMailNotificationError()
            return True
        except Exception as exception:
            if event.support_email_address:
                report_message = ''
                for key, value in data.items():
                    report_message += f'<p>{key}: {value}</p>'
                event.send_support(
                    subject="Не удалось добавить в гугл таблицу информацию о регистрации!",
                    message=f"<p>Ошибка: {type(exception)} | {exception}</p>\n" + report_message
                )
            return False
