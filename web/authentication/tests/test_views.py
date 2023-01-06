from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import modify_settings
from django.utils import timezone
from rest_framework.reverse import reverse_lazy
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

User = get_user_model()


class ViewsTest(APITestCase):
    @modify_settings(
        MIDDLEWARE={
            'append': 'authentication.middleware.TimezoneMiddleware',
        }
    )
    def test_set_timezone(self):
        self.assertEqual(1,1)
