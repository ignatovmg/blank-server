from django.core.mail import send_mail
from . import env


def send_greeting(user):
    """
    Send a friendly message to a new user
    :param `django.contrib.auth.models.User` user: Receiver
    """
    message = 'Thank you for joining {}!\n\nYour username is {}.'.format(env.SERVER_NAME, user.username)
    server_email = 'noreply'
    send_mail('User created on {}'.format(env.SERVER_NAME),
              message,
              server_email,
              [user.email],
              fail_silently=False)
