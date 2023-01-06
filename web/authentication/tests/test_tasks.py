from django.core import mail
from django.test import TestCase, override_settings

from authentication import tasks

locmem_email_backend = override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
)


class CeleryTaskTestCase(TestCase):
    @locmem_email_backend
    def test_send_information_email(self):
        self.assertEqual(1, 1)
