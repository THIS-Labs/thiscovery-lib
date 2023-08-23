from http import HTTPStatus

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Cc, Bcc, Category

from thiscovery_lib.utilities import get_secret


class EmailError(Exception):
    pass


class SendGridClient:
    """
    Utilitly client for sending email via our SendGrid account.
    """

    def __init__(self, sending_data, template_data, template_id, environment):
        """
        args:
            sending_data (dict): contains the email and name of the email receipient
            template_data (dict): contains data used to populate variables in
                the email template
            template_id (string): the id of the template to use for this email
            environment (string): the name of the environment the email is being
                sent from. This is used to categorise emails in SendGrid.
        """
        self.sendgrid_api_client = SendGridAPIClient(self._get_api_key())
        self.mail = self._create_message(sending_data, template_data, template_id, environment)

    def _create_message(self, sending_data, template_data, template_id, environment):
        """
        Accepts all the same arguments as the __init__ method and uses them to
        build the email which will be sent.
        """
        mail = Mail()
        mail.add_to((sending_data["email"], sending_data["name"]))

        ccs = sending_data.get("cc", [])
        for cc in ccs:
            mail.add_cc(Cc(cc))

        bccs = sending_data.get("bcc", [])
        for bcc in bccs:
            mail.add_cc(Bcc(bcc))

        # Sendgrid templates have a bug which means that
        # sender template variables don't work, so we
        # insert them here from a secret.
        sender_data = get_secret("sendgrid-sender-data")
        template_data.update(sender_data)

        mail.from_email = sending_data["from_email"]
        mail.reply_to = sending_data["reply_to"]
        mail.template_id = template_id
        mail.dynamic_template_data = template_data
        mail.add_category(Category(environment))

        return mail

    def _get_api_key(self):
        return get_secret("sendgrid-api-key")

    def send_email(self):
        response = self.sendgrid_api_client.send(self.mail)

        if response.status_code != HTTPStatus.ACCEPTED:
            raise EmailError(
                f"Unexpected status code: {response.status_code}. We received this from SendGrid: {response.body}"
            )

        return response
