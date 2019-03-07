from django.core.mail import send_mail
from . import env


def send_greeting(user):
    message = 'Thank you for joining {}'.format(env.SERVER_NAME)

    send_mail('User created on {}'.format(env.SERVER_NAME),
              message, 'brikard.server@gmail.com', [user.email], fail_silently=False)


