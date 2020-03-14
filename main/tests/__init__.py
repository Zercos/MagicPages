from unittest.mock import patch


class MockSendContactEmail:
    def setUp(self):
        self.send_mail_to_customer_service_patch = patch('main.tasks.send_mail_to_customer_service')
        self.send_mail_to_customer_service_mock = self.send_mail_to_customer_service_patch.start()
        super().setUp()

    def tearDown(self):
        self.send_mail_to_customer_service_patch.stop()
        self.send_mail_to_customer_service_mock = None
        super().tearDown()
