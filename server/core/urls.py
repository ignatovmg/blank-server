from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('index', views.index, name='index'),
    path('login', views.login_page, name='login'),
    path('queue', views.queue_page, name='queue'),
    path('results', views.results_page, name='results'),
    path('publications', views.publications_page, name='publications'),
    path('help', views.help_page, name='help'),
    path('contact', views.contact_page, name='contact'),
    path('signup', views.signup_page, name='signup'),
    path('logout', views.logout_page, name='logout'),
    path('details', views.details_page, name='details'),
    path('thankyou', views.thankyou_page, name='thankyou')
]
