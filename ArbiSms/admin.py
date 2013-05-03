from django.contrib import admin
from sms.models import Server, Jobs

class ServerAdmin(admin.ModelAdmin):
    pass


class JobsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Server, ServerAdmin)
admin.site.register(Jobs, JobsAdmin)