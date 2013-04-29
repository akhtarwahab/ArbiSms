from django.contrib.auth.models import User
from django.db import models


class Server(models.Model):
    user = models.ForeignKey(User)
    server_name = models.CharField(max_length=140)
    server_address = models.CharField(max_length=2048)
    creation_date = models.DateTimeField(auto_now=True, blank=True)

class Jobs(models.Model):
    user = models.ForeignKey(User)
    server = models.ForeignKey(Server)
    server_name = models.CharField(max_length=140)
    start_date_time = models.DateTimeField(auto_now=True, blank=True)
    end_date_time = models.DateTimeField(auto_now=True, blank=True)
    job_id = models.CharField(max_length=140)
    project = models.CharField(max_length=140)
    spider = models.CharField(max_length=140)
    log = models.CharField(max_length=140)
    items = models.CharField(max_length=140)
