import json
from django.core.files.uploadedfile import InMemoryUploadedFile
from googleapiclient.discovery import build
from google.oauth2 import service_account
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient, APIVersion
from django.conf import settings


class GoogleDrive:
    drive_service = None

    def __init__(self, credential_filename):
        credentials = service_account.Credentials.from_service_account_file(
            filename=credential_filename,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive_service = build('drive', 'v3', credentials=credentials)

    def get_files(self,
                  q="mimeType='application/vnd.google-apps.folder'",
                  fields='nextPageToken, files(id, name, mimeType)'):
        return self.drive_service.files().list(q=q, fields=fields).execute()

    def create_folder(self, name: str, folder_id: str = None):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]

        return self.drive_service.files().create(body=file_metadata).execute().get('id')

    def create_file(self, file: InMemoryUploadedFile, file_name: str = None, folder_id: str = None):
        if not file_name:
            file_name = file.name
        elif not Path(file_name).suffix:
            file_name = file_name + Path(file.name).suffix

        file_path = default_storage.save(f'tmp/{folder_id}/{file_name}', ContentFile(file.read()))

        # file_metadata = {
        #     'name': file_name,
        # }
        # if folder_id:
        #     file_metadata['parents'] = [folder_id]
        #
        # media = MediaFileUpload(file_path, mimetype=file.content_type, resumable=True)
        # file_id = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute().get(
        #     'id')
        return file_path


class MicrosoftGraph:
    graph_client = None

    @staticmethod
    def get_client():
        credential = ClientSecretCredential(
            client_id=settings.MICROSOFT_APP_CLIENT_ID,
            tenant_id=settings.MICROSOFT_APP_TENANT_ID,
            client_secret=settings.MICROSOFT_APP_CLIENT_SECRET,
            redirect_uri='http://localhost:8450'
        )
        return GraphClient(credential=credential, api_version=APIVersion.v1)

    @classmethod
    def send_mail(cls, from_address: str, to_address: str,  message: str, subject: str = ""):
        client = cls.get_client()

        body = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": message
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_address
                        }
                    }
                ],
            },
            "saveToSentItems": "true"
        }

        result = client.post(url=f'/users/{from_address}/sendMail',
                             data=json.dumps(body),
                             headers={'Content-Type': 'application/json'})
        return result.ok
