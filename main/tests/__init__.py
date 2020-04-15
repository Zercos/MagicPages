from unittest.mock import patch


class MockSendContactEmail:
    def setUp(self):
        self.send_mail_celery_patch = patch('main.forms.tasks.send_email')
        self.send_mail_celery_mock = self.send_mail_celery_patch.start()
        super().setUp()

    def tearDown(self):
        self.send_mail_celery_patch.stop()
        self.send_mail_celery_mock = None
        super().tearDown()
