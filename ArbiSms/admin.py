from django.contrib import admin
from sms.models import Server, Jobs

__author__ = 'Akhter Wahab'


class ServerAdmin(admin.ModelAdmin):
    pass


class JobsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Server, ServerAdmin)
admin.site.register(Jobs, JobsAdmin)