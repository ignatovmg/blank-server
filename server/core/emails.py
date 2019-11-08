from django.core.mail import send_mail
from . import env


def send_greeting(user, password):
    """
    Send a friendly message to a new user
    :param `django.contrib.auth.models.User` user: Receiver
    :param str password: Password
    """
    message = 'Thank you for joining {}!\n\nYour username is\n\n\t{}\n\nand your password is\n\n\t{}\n'.format(env.SERVER_NAME, user.username, password)
    server_email = None
    send_mail('User created on {}'.format(env.SERVER_NAME),
              message,
              server_email,
              [user.email],
              fail_silently=False)


def send_password(user, password):
    """
    Send a new password
    :param `django.contrib.auth.models.User` user: Receiver
    :param str password: Password
    """

    message = 'Dear {},\n\nYour new password is:\n\n\t{}\n\nIf you didn\'t request a password reset, please contact us.'.format(user.username, password)
    server_email = None
    send_mail('Password reset for {}'.format(env.SERVER_NAME),
              message,
              server_email,
              [user.email],
              fail_silently=False)


def send_username(user):
    """
    Send a new password
    :param `django.contrib.auth.models.User` user: Receiver
    """

    message = 'Dear user,\n\nYou requested a username reminder. Your username is \n\n{}\n'.format(user.username)
    server_email = None
    send_mail('Your username for {}'.format(env.SERVER_NAME),
              message,
              server_email,
              [user.email],
              fail_silently=False)
