# Server template
Django + Postgre + Bootstrap server template (in development).
 
### HOWTO
1. Install the requirements.
2. Create a Postgre database
3. Copy example.config to ~/.template_server_rc and specify 
database credentials (also change email settings). Remote 
settings are not effective yet
4. Populate databases \
`python manage.py makemigrations`\
`python manage.py migrate`
5. Create superuser \
`python manage.py createsuperuser --name admin`
6. Run server \
`python manage.py runserver`\
or if you want to use a specific port\
`python manage.py runserver 8000`
7. Check if admin site works\
`localhost:8000/admin`
8. Read Django tutorial for further development

### Some details
This is a server shell. The frontend is located in `core/`, so the machinery 
should be put in a separate directory `runner/` in the form of a python package.

