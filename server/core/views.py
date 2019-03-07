import logging

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

from .models import Job
from .job_handling import check_job_input, create_job_dir, submit_job
from . import env
from . import forms
from . import emails

logger = logging.getLogger(__name__)


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
            err_dict = form.errors.get_json_data(escape_html=True)
            errors += ['{}: {}'.format(k, v[0]['message']) for k, v in err_dict.items()]
        else:
            errs, tmp_dir = check_job_input(request)
            errors += errs

        if not errors:
            job = Job(user=request.user,
                      ip=_get_client_ip(request),
                      status="L.STR",
                      job_name=form.cleaned_data['jobname'])
            job.save()
            job.save()

            logger.info('Preparing job ..')
            create_job_dir(tmp_dir, job.job_id)

            submit_job(job)

            return redirect('queue')

    else:
        form = forms.JobSubmitForm()

    return render(request, 'core/home.html', {'errors': errors, 'form': form})


@login_required(login_url='login')
def queue_page(request):
    job_list = Job.objects.exclude(status__exact='L.CPL')
    if not request.user.is_superuser:
        job_list = job_list.filter(user__username=request.user.username)

    paginator = Paginator(job_list, env.JOBS_PER_PAGE)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    return render(request, 'core/jobs.html', {'jobs': jobs})


@login_required(login_url='login')
def results_page(request):
    job_list = Job.objects.filter(status__exact='L.CPL')
    if not request.user.is_superuser:
        job_list = job_list.filter(user__username=request.user.username)

    paginator = Paginator(job_list, env.JOBS_PER_PAGE)
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


def reject_access(request):
    raise PermissionDenied('Sorry, you don\'t have a permission to access this page')


def publications_page(request):
    return render(request, 'core/publications.html')


def help_page(request):
    return render(request, 'core/help.html')


def contact_page(request):
    return render(request, 'core/contact.html')


def signup_page(request):
    errors = []

    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)

        if form.is_valid():
            user = User(username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'])
            try:
                user.save()
            except IntegrityError as e:
                errors.append('Provided username already exists, please pick a different one')
            else:
                emails.send_greeting(user)
                return redirect('thankyou')
        else:
            err_dict = form.errors.get_json_data(escape_html=True)
            errors += ['{}: {}'.format(k, v[0]['message']) for k, v in err_dict.items()]
    else:
        form = forms.SignUpForm()

    return render(request, 'core/signup.html', {'form': form, 'errors': errors})


def thankyou_page(request):
    return render(request, 'core/thankyou.html')


def login_page(request):
    logout(request)

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

