# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid

# Create your models here.

class Query(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(blank=True)
    name = models.CharField(max_length=100, default='Default_Query_Name')
    sequence = models.TextField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('auth.User', related_name='queries', on_delete=models.CASCADE)
    class Meta:
        ordering = ['created']

class Job(models.Model):
    STATUSES = (
        ('CR', 'Created'),
        ('IP', 'In Progress'),
        ('CO', 'Completed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(blank=True)
    name = models.CharField(max_length=100, default='Default_Job_Name')
    query = models.ForeignKey(Query, null=True,related_name='jobs', on_delete=models.CASCADE )
    status = models.CharField(max_length=2, choices=STATUSES)
    location = models.URLField(default='swift.example.com/object1')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    backend_job = models.TextField(null=True)

    def save(self, *args, **kwargs):
        self.backend_job = "job started!"
        super(Job, self).save(*args, **kwargs)

    class Meta:
        ordering = ['start_time']







