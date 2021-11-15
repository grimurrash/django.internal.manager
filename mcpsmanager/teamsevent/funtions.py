from azure.identity import ClientSecretCredential
from django.conf import settings
from msgraph.core import GraphClient, APIVersion


def transliterate(name: str):
    name = name.lower()
    # Слоаврь с заменами
    words = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
             'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
             'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
             'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
             'ю': 'u', 'я': 'ja', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
             'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
             'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
             'Ц': 'C', 'Ч': 'CZ', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
             'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
             '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
             ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
             '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
             'Є': 'e', '—': ''}
    result_string = ''
    for key in name:
        translate_key = words.get(key)
        if not translate_key:
            translate_key = key
        result_string += translate_key
    return result_string


def get_client():
    # credential = InteractiveBrowserCredential(
    #     client_id=settings.MICROSOFT_APP_CLIENT_ID,
    #     tenant_id=settings.MICROSOFT_APP_TENANT_ID,
    #     redirect_uri='http://localhost:8450'
    # )

    credential = ClientSecretCredential(
        client_id=settings.MICROSOFT_APP_CLIENT_ID,
        tenant_id=settings.MICROSOFT_APP_TENANT_ID,
        client_secret=settings.MICROSOFT_APP_CLIENT_SECRET,
        redirect_uri='http://localhost:8450'
    )

    client = GraphClient(credential=credential,
                         api_version=APIVersion.v1)
    return client
