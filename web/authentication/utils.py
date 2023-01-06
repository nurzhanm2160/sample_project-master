from typing import Any

from django.utils.translation import get_language_from_request

from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
import uuid
import string
import random


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()


def generate_code():
    code = get_random_string(15).upper()
    return code



def parse_str_with_space(var: str) -> str:
    """return string without multiply whitespaces
    Example: var = 'My name  is   John    '
    Return var = 'My name is John'
    """
    str_list = list(filter(None, var.split(' ')))
    return ' '.join(x for x in str_list)


def find_dict_in_list(target: list[dict], dict_key: str | int, lookup_value: Any) -> dict:
    """Find a dict in a list of dict by dict key"""
    return next(iter(x for x in target if x.get(dict_key) == lookup_value), {})


def get_supported_user_language(request) -> str:
    return get_language_from_request(request)
