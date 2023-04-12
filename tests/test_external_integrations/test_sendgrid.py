from http import HTTPStatus

import local.dev_config
import local.secrets

from unittest import TestCase
from unittest.mock import patch, MagicMock

from thiscovery_lib.sendgrid_utilities import EmailError, SendGridClient


class TestSendGridClient(TestCase):
    def setUp(self):
        with patch("thiscovery_lib.sendgrid_utilities.get_secret"):
            self.sendgrid_client = SendGridClient(
                sending_data={
                    "email": "test@example.org",
                    "name": "test",
                    "from_email": ("thiscovery@thisinstitute.cam.ac.uk", "thiscovery"),
                    "reply_to": ("thiscovery@thisinstitute.cam.ac.uk", "thiscovery"),
                },
                template_data={"first_name": "Test"},
                template_id="d-123",
            )

    def test_client(self):
        assert self.sendgrid_client is not None

    @patch("thiscovery_lib.sendgrid_utilities.SendGridAPIClient.send")
    def test_send_email(self, mocked_send):
        mocked_response = MagicMock()
        mocked_response.status_code = HTTPStatus.ACCEPTED
        mocked_send.return_value = mocked_response

        self.sendgrid_client.send_email()
        mocked_send.assert_called()

    def test_create_message(self):
        mail = self.sendgrid_client._create_message(
            sending_data={
                "email": "test@example.org",
                "name": "test",
                "from_email": ("thiscovery@thisinstitute.cam.ac.uk", "thiscovery"),
                "reply_to": ("thiscovery@thisinstitute.cam.ac.uk", "thiscovery"),
                "bcc": ["test@example.org"],
                "cc": ["test2@example.org"],
            },
            template_data={"first_name": "Test"},
            template_id="d-123",
        )

        assert mail.personalizations[0].tos[0].get("email") == "test@example.org"
        assert mail.personalizations[0].tos[0].get("name") == "test"
        assert mail.personalizations[0].bccs[0].get("email") == "test@example.org"
        assert mail.personalizations[0].ccs[0].get("email") == "test2@example.org"
        assert mail.from_email.email == "thiscovery@thisinstitute.cam.ac.uk"
        assert mail.from_email.name == "thiscovery"
        assert mail.reply_to.email == "thiscovery@thisinstitute.cam.ac.uk"
        assert mail.reply_to.name == "thiscovery"
        assert mail.template_id is not None

    def test_send_email_error(self):
        with patch(
            "thiscovery_lib.sendgrid_utilities.SendGridAPIClient.send"
        ) as mocked_send:
            mocked_response = MagicMock()
            mocked_response.status_code = HTTPStatus.BAD_REQUEST
            mocked_send.return_value = mocked_response

            with self.assertRaises(EmailError):
                self.sendgrid_client.send_email()
