# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid

# Create your models here.

class Query(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    name = models.CharField(max_length=100, default='Default_Job_Name')
    query = models.ForeignKey(Query, null=True,related_name='jobs', on_delete=models.CASCADE )
    status = models.CharField(max_length=2, choices=STATUSES)
    yarn_id = models.CharField(max_length=100,null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.backend_job = "job started!"
        super(Job, self).save(*args, **kwargs)

    class Meta:
        ordering = ['start_time']

class Dataset(models.Model):
    name = models.CharField(max_length=100, primary_key=True, null=False)
    jobs = models.ManyToManyField(Job, null=True,related_name='datasets')
    creator = models.ForeignKey('auth.User', related_name='datasets', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s' % (self.name)

    class Meta:
        ordering = ['created']

class Raw(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datum = models.ForeignKey(Dataset, related_name="raw_data", on_delete=models.CASCADE, null=False)
    location = models.URLField(null=False, blank=False)

    def __unicode__(self):
        return '%s' % (self.location)





