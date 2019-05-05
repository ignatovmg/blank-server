from django.core.mail import send_mail
from . import env


def send_greeting(user):
    """
    Send a friendly message to a new user
    :param `django.contrib.auth.models.User` user: Receiver
    """
    message = 'Thank you for joining {}!\n\nYour username is "{}".'.format(env.SERVER_NAME, user.username)
    server_email = 'noreply'
    send_mail('User created on {}'.format(env.SERVER_NAME),
              message,
              server_email,
              [user.email],
              fail_silently=False)


def send_password(user, password):
    """
    Send a new password
    :param `django.contrib.auth.models.User` user: Receiver
    """

    message = 'Dear {},\n\nYou requested a password reset. Your new password is "{}".\n'.format(user, password)
    server_email = 'noreply'
    send_mail('Password reset for {}'.format(env.SERVER_NAME),
              message,
              server_email,
              [user.email],
              fail_silently=False)


def send_username(user, username):
    """
    Send a new password
    :param `django.contrib.auth.models.User` user: Receiver
    """

    message = 'Dear {},\n\nYou requested a username reminder.\n'.format(user)
    server_email = 'noreply'
    send_mail('Your username for {}'.format(env.SERVER_NAME),
              message,
              server_email,
              [user.email],
              fail_silently=False)
