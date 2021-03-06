from django.core.mail import EmailMessage
from django.conf import settings
import threading
class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()
class Utils:
    @staticmethod
    def send_email(data):
        email = EmailMessage(data['email_subject'],
        data['email_body'], settings.EMAIL_HOST_USER,[data["to"]])
        EmailThread(email).start()