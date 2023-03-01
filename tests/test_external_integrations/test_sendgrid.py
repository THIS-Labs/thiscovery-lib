import local.dev_config
import local.secrets

from unittest import TestCase
from unittest.mock import patch, MagicMock

from thiscovery_lib.sendgrid_utilities import SendGridClient


class TestSendGridClient(TestCase):
    def setUp(self):
        with patch("thiscovery_lib.sendgrid_utilities.get_secret"):
            self.sendgrid_client = SendGridClient(
                {"email": "test@example.org", "name": "test"},
                {"first_name": "Test"},
                "d-123",
            )

    def test_client(self):
        assert self.sendgrid_client is not None

    @patch("thiscovery_lib.sendgrid_utilities.SendGridAPIClient.send")
    def test_send_email(self, mocked_send):
        mocked_response = MagicMock()
        mocked_response.status_code = 202
        mocked_send.return_value = mocked_response

        self.sendgrid_client.send_email()
        mocked_send.assert_called()

    def test_create_message(self):
        mail = self.sendgrid_client._create_message(
            {"email": "test@example.org", "name": "test"},
            {"first_name": "hello"},
            "d-123",
        )

        assert mail.personalizations[0].tos[0].get("email") == "test@example.org"
        assert mail.personalizations[0].tos[0].get("name") == "test"
        assert mail.from_email.email == "thiscovery@thisinstitute.cam.ac.uk"
        assert mail.from_email.name == "thiscovery"
        assert mail.reply_to.email == "thiscovery@thisinstitute.cam.ac.uk"
        assert mail.reply_to.name == "thiscovery"
        assert mail.template_id is not None
