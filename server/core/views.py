import logging
import json

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password

from .models import Job
from .job_handling import check_user_input, create_job_dir, submit_job
from . import env
from . import forms
from . import emails
from . import utils

logger = logging.getLogger('core')


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required(login_url='login')
def index(request):
    errors = []

    if request.method == 'POST':
        form = forms.JobSubmitForm(request.POST)

        if not form.is_valid():
            err_dict = form.errors.get_json_data(escape_html=False)
            errors += ['{}'.format(v[0]['message']) for k, v in err_dict.items()]
        else:
            errs, tmp_dir = check_user_input(request)
            errors += errs

            if not errors:
                job = Job(user=request.user,
                          ip=_get_client_ip(request),
                          status="L.STR",
                          job_name=form.cleaned_data['jobname'])
                job.save()

                create_job_dir(tmp_dir, job.job_id)

                clean_json = job.get_user_json()
                with open(clean_json, 'r') as f:
                    details_json = json.load(f)
                job.details_json = json.dumps(details_json)
                job.status = 'L.STR'
                job.save()

                submit_job(job.job_id)
                return redirect('queue')

    else:
        form = forms.JobSubmitForm()

    return render(request, 'core/home.html', {'errors': errors, 'form': form})


@login_required(login_url='login')
def restart_job(request):
    job_id = int(request.GET.get('job_id'))
    errors = submit_job(job_id)

    if not errors:
        return redirect('queue')

    return HttpResponse('<h1>' + errors[0] + '</h1>')


@login_required(login_url='login')
def queue_page(request):
    job_list = Job.objects.exclude(status__in=['L.CPL', 'R.ERR', 'L.ERR'])
    if not request.user.is_superuser:
        job_list = job_list.filter(user__username=request.user.username)

    paginator = Paginator(job_list.order_by('-job_id'), env.JOBS_PER_PAGE)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    return render(request, 'core/jobs.html', {'jobs': jobs})


@login_required(login_url='login')
def results_page(request):
    job_list = Job.objects.filter(status__in=['L.CPL', 'R.ERR', 'L.ERR'])
    if not request.user.is_superuser:
        job_list = job_list.filter(user__username=request.user.username)

    paginator = Paginator(job_list.order_by('-job_id'), env.JOBS_PER_PAGE)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    return render(request, 'core/jobs.html', {'jobs': jobs})


@login_required(login_url='login')
def details_page(request):
    job_id = request.GET.get('job_id')
    job = Job.objects.get(job_id=job_id)
    user = request.user

    if not request.user.is_superuser and job.user.id != user.id:
        reject_access(request)

    return render(request, 'core/details.html', {'job': job})


@login_required(login_url='login')
def download_file(request):
    user = request.user
    job_id = request.GET.get('job_id')
    content = request.GET.get('content')
    job = Job.objects.get(job_id=job_id)

    if not request.user.is_superuser and job.user.id != user.id:
        reject_access(request)

    output_dir = job.get_output_dir()
    if content == 'output.txt':
        file_path = output_dir.joinpath(content)
        response = HttpResponse(content_type='plain/text')
    else:
        raise Http404('Wrong content type')

    response['Content-Disposition'] = 'attachment; filename="{}"'.format(content)
    with open(file_path, 'rb') as f:
        response.write(f.read())

    return response


def reject_access(request):
    raise PermissionDenied('Sorry, you don\'t have a permission to access this page')


def publications_page(request):
    return render(request, 'core/publications.html')


def help_page(request):
    return render(request, 'core/help.html')


def contact_page(request):
    return render(request, 'core/contact.html')


def signup_page(request):  # TODO: add second password field
    logout(request)

    context = {'page_title': 'Sign Up',
               'page_description': '',
               'submit_text': 'Sign Up'}

    errors = []

    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)

        if not form.is_valid():
            err_dict = form.errors.get_json_data(escape_html=False)
            errors += ['{}: {}'.format(k, v[0]['message']) for k, v in err_dict.items()]
        else:
            new_password = utils.random_string(10)
            user = User(username=form.cleaned_data['username'],
                        password=make_password(new_password),
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'])
            try:
                user.save()
            except IntegrityError as e:
                errors.append('Provided username already exists, please pick a different one')
            else:
                emails.send_greeting(user, new_password)
                return redirect('thankyou')

    else:
        form = forms.SignUpForm()

    context.update({'form': form, 'errors': errors})
    return render(request, 'core/generic_form.html', context)


def thankyou_page(request):
    return render(request, 'core/thankyou.html')


def login_page(request):
    logout(request)

    if request.GET.get('anon') == 'true':
        username = 'anon'
        password = '97531anonymous13579'
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'core/login.html', {'errors': ['Cannot use anonymous login due to internal error']})

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'core/login.html', {'errors': ['Invalid username or password']})

    return render(request, 'core/login.html')


def logout_page(request):
    logout(request)
    return redirect('login')


def reset_password_page(request):
    logout(request)

    context = {'page_title': 'Reset password',
               'page_description': 'We will send you a new password to the e-mail address, associated with the provided username',
               'submit_text': 'Reset password'}

    errors = []
    messages = []
    form = forms.PasswordResetForm()

    if request.method == 'POST':
        form = forms.PasswordResetForm(request.POST)

        if not form.is_valid():
            err_dict = form.errors.get_json_data(escape_html=False)
            errors += ['{}'.format(v[0]['message']) for k, v in err_dict.items()]
        else:
            try:
                new_password = utils.random_string(10)
                username = form.cleaned_data['username']
                user = User.objects.get(username=username)
                user.set_password(new_password)
                emails.send_password(user, new_password)
            except Exception as e:
                logging.exception(e)
                errors += ['Internal error has occured. Please contact us to solve the issue.']
            else:
                user.save()
                messages += ['Your password was successfully reset, please check your e-mail.']
                return render(request, 'core/login.html', {'messages': messages, 'form': form})

    context.update({'form': form, 'errors': errors})
    return render(request, 'core/generic_form.html', context)


def retrieve_username_page(request):
    logout(request)

    context = {'page_title': 'Retrieve username',
               'page_description': 'We will send your username to the e-mail address you specified at sign-up',
               'submit_text': 'Remind me my username'}

    errors = []
    messages = []
    form = forms.RetrieveUsernameForm()

    if request.method == 'POST':
        form = forms.RetrieveUsernameForm(request.POST)

        if not form.is_valid():
            err_dict = form.errors.get_json_data(escape_html=False)
            errors += ['{}'.format(v[0]['message']) for k, v in err_dict.items()]
        else:
            try:
                email = form.cleaned_data['email']
                user = User.objects.get(email=email)
                emails.send_username(user)
            except Exception as e:
                logging.exception(e)
                errors += ['Internal error has occured. Please contact us to solve the issue.']
            else:
                user.save()
                messages += ['Your username was sent to your e-mail address.']
                return render(request, 'core/login.html', {'messages': messages, 'form': form})

    context.update({'form': form, 'errors': errors})
    return render(request, 'core/generic_form.html', context)


@login_required(login_url='login')
def settings_page(request):
    if request.user.username == "anon":
        reject_access(request)

    context = {'page_title': 'Settings',
               'page_description': 'Change your account preferences here',
               'submit_text': 'Save changes'}

    errors = []
    messages = []
    form = forms.SettingsForm()
    if request.method == 'POST':
        form = forms.SettingsForm(request.POST)
        if not form.is_valid():
            err_dict = form.errors.get_json_data(escape_html=False)
            errors += ['{}'.format(v[0]['message']) for k, v in err_dict.items()]
        else:
            if not request.user.check_password(form.cleaned_data['current_password']):
                errors += ['Wrong password provided']
            else:
                new_password = form.cleaned_data['password']
                try:
                    request.user.set_password(new_password)
                    request.user.save()
                except Exception as e:
                    logger.exception(e)
                    errors += ['Internal error occured']
                else:
                    messages += ['Your changes were successfully applied']
                    context.update({'form': form, 'messages': messages})
                    return render(request, 'core/generic_form.html', context)

    context.update({'form': form, 'errors': errors})
    return render(request, 'core/generic_form.html', context)
