# Server template
Django + Postgres + Bootstrap (in development).

### Getting started
1. [Install Docker Community Edition](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)    
2. Install docker-compose into python3, e.g. `pip3 install --user docker-compose`    
3. Add your user to the docker group. `sudo usermod -a -G docker username` ; 
you may have to reboot after this step for you to show up in the group.    
    
You should then use the `local-docker-compose` script as a drop in replacement 
for docker-compose. For example, to start the server you can 
run `local-docker-compose up --build`.    

Cleaning up after docker for a clean rebuild:     
1. `./cluspro-docker-compose rm` will remove the containers       
2. `docker volume prune`

If you don't explicitly remove the volumes between docker runs, the databases persist, 
so you can stop the containers and launch them again safely without any loss of data.

### Overview
This is a server shell, which has all administration machinery (manage users, jobs, 
databases etc.) and also a way to run jobs. It is intended to be run via docker.    

#### Three-tier architecture
Docker runs 3 services: web (which runs Gunicorn), nginx and db (Postgres database). 
Gunicorn handles the python (Django) code, accesses the database and cooperates with Nginx. 

#### Project stucture
All the frontend code is located in `server/`.
The structure of `server/` directory is enforced by the Django rules, so we have
`server/server`, where all the server settings locate (`settings.py`) as well as `config.py`. 
`config.py` is where the custom variables are kept (e.g. email login 
 and password for sending messages to the user), which in turn are populated from 
 the environment, which is set in docker-compose.yml.     
`core/` contains the app code, as it's called in Django. `core/templates` has all 
the html files, `core/static` - CSS and JS, and `runner/` is a shell for your job 
running code. Right now it contains a fake job running function, which doesn't 
do much.

The backend code is located in `backend/`. You must manually copy its content to the 
backend server site to the directory you specified, when prompted at the first launch of 
`local-docker-compose` ("Binary directory on the remote machine"). It will be copied 
automatically in the future.

#### `Core/` structure
1. `views.py` is the main file - it contains all the page renderers and handles 
all the forms and requests. Most of functions return an HTML response.

2. `urls.py` assigns URLs to the functions in `views.py`.

3. `models.py` contains custom data tables, which are added to the default Django
tables. Right now it contains a model for jobs, which can be customized as you wish.
The intention, however, was to keep all the generic job fields as separate class attributes
(job name, IP etc.) and to store all the rest job-type specific parameters as a json string
in details_json field. This way we can prevent creating many different tables for different 
job types or addition of infinite new fields to the same job table (once we add new job parameters, 
for example).

4. `job_handling.py` should contain all the functions, which have to do with 
launching jobs (however the actual job running code should be put in `runner/`).

5. All the forms, which are on the website are contained in `forms.py` and it should
be kept so. These forms are all handled in `views.py`.

6. `emails.py` has messages for users, whenever we want to send them something. They
use the e-mail address and password specified in `server/settings.py`, which are in 
turn taken from environmental variables in `docker-compose.yml`. If they were not 
specified you will get an error, whenever the server is trying to send a message.

7. `env.py` is where you should keep your local variables. Also all the variables
 in `env` dictionary will be passed as a context to the html templates, so you 
 can refer to them in the templates.
 
#### At the first launch
Two users are created. 
1) admin with password 'admin'. This is a superuser, you should change the 
password for it immediately. The admin page is located at http://localhost/admin
2) anon, which is where you log in once you click 'use without your own account' 
button on the login page. It has limited permissions.

#### Jobs
When you run jobs they are stored in docker container in `/storage`, which is 
by default mounted in your project root. You can change this in `docker-compose.yml`.
Storage has two directories: `tmp/` for temporary storage, if you need to compute
or check something before adding the job to the database, and `jobs/` with all
the jobs.

#### .local_params
Environmental variables with some paths, e-mail login and password are stored 
in `.local_params`, which is created, when you first run `local-docker-compose.py`. 
Those variable prefixed with REMOTE_ are needed, if you want to run your jobs via 
ssh. They are not used in any way right now, and you will have to add all the remote
execution yourself. LOCAL_PORT is the port through which you access the server and 
SECRET_KEY is for Django internal use (is generated at the first run 
of `local-docker-compose`) and should be kept secret.

### Development
As a next step you should go to Django page and read tutorials.

