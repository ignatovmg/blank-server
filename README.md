# Template server
#### A server shell for you to play with    
Powered by Django + Nginx + Postgres + Bootstrap + Celery.

------
### Getting started
1. [Install Docker Community Edition](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)    
2. Install docker-compose into python3, e.g. `pip3 install --user docker-compose`    
3. Add your user to the docker group. `sudo usermod -a -G docker username` ; 
you may have to reboot after this step for you to show up in the group.    
4. Create a file `.local_params` in the root directory using `.local_params_examples` as a template.
Read section "Running jobs" for the details.

    
You should then use the `local-docker-compose` script as a drop in replacement 
for docker-compose. For example, to start the server you can 
run `local-docker-compose up --build`.

Cleaning up after docker for a clean rebuild:     
1. `./cluspro-docker-compose rm` will remove the containers       
2. `docker volume prune`

If you don't explicitly remove the volumes between docker runs, the databases persist, 
so you can stop the containers and launch them again safely without any loss of data.

#### Architecture
Docker runs several services: web (which runs Gunicorn), nginx, db (Postgres database). 
Gunicorn handles the python (Django) code, accesses the database and cooperates with Nginx.
Celery is a background task manager and it need rabbitMQ to run (message broker). Flower is
a task monitor, which is powered by Celery. It can be accessed at localhost:5555

#### Structure
All the frontend code is located in `server/`.
The structure of `server/` directory is enforced by the Django rules, so we have
`server/server`, where all the server settings are located (`settings.py`) as well as `config.py`. 
`config.py` is where the custom variables are kept (e.g. email login 
 and password for sending messages to the user), which in turn are populated from 
 the environment, which is set in docker-compose.yml.     
`core/` contains the app code, as it's called in Django. `core/templates` has all 
the html files, `core/static` - CSS and JS, and `runner/` contains the code for job 
running.

#### `Core/` structure
1. `views.py` is the main file - it has functions, which render the pages and handle 
all the forms and requests. Most of functions return an HTML response.

2. `urls.py` assigns URLs to the functions in `views.py`.

3. `models.py` contains custom data tables, which are added to the default Django
tables. Right now it contains a model for jobs, which can be customized as you wish.
The intention, however, was to keep all the generic job fields as separate class attributes
(job name, IP etc.) and to store all the rest job specific parameters as a json string
in details_json field. This way we can prevent creating many different tables for different 
job types or addition of infinite new fields to the same job table (once we add new job parameters, 
for example).

4. All the forms on the website are contained in `forms.py` and it should
be kept so. These forms are all handled in `views.py`.

5. `emails.py` has messages for users, whenever we want to send them something. They
use the e-mail address and password specified in `server/settings.py`, which are in 
turn taken from environmental variables in `docker-compose.yml`. If they were not 
specified you will get an error, whenever the server is trying to send a message.

6. `env.py` is where you should keep your local variables. Also all the variables
 in `env` dictionary will be passed as a context to the html templates, so you 
 can refer to them in the templates.
 
#### At the first launch
Two users are created.    

1. admin with password 'admin'. This is a superuser, you should change the 
password for it immediately. The admin page is located at http://localhost:8080/admin     
2. anon, which is where you log in once you click 'use without your own account' 
button on the login page. It has limited permissions.   
    
Also `storage/` directory is created in the root, where all the jobs will be kept.

#### Jobs
When you run jobs they are stored in docker container in `/storage`, which is 
by default mounted in your project root. You can change this in `docker-compose.yml`.
Storage has two directories: `tmp/` for temporary storage, if you need to compute
or check something before adding the job to the database, and `jobs/` with all
the jobs.

-----
### Running jobs
#### Jobs
Currently a job performs addition of two integer numbers. Some additional requirements are added to 
demonstrate how to use error pop-ups etc. The task itself is located in `models.py`.

#### .local_params
Environmental variables with some paths, e-mail login and password are stored 
in `.local_params`, which are used when you run `local-docker-compose`. To create the 
file use `.local_params_example` as a template.  
     
Variables for sending e-mails. If you don't specify them, everything will still run, but you will 
get errors when new users register etc.
If your e-mail is `server@gmail.com` and the password is `password` then the values should be:   
      
`EMAIL_USER` - server    
`EMAIL_PASS` - password     
`EMAIL_HOST` - smtp.gmail.com
      
`FLOWER_USER` and `FLOWER_PASS` will be generated and added to `.local_params` at the first run of `local-docker-compose`, unless 
 specified by the user.
     
`LOCAL_PORT` is the port, through which you access the server (default is `8080`)
     
`SECRET_KEY` is for Django internal use (is generated at the first run 
of `local-docker-compose`) and should be kept secret.
