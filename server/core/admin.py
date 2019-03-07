from django.contrib import admin

from .models import Job

#class CustomAdmin(admin.ModelAdmin):
#    list_display = ("created", )

#admin.site.register(Job, CustomAdmin)
admin.site.register(Job)