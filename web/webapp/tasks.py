# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import task


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@task(name="submit_spark_job")
def submit_spark_job():
    print 'hi'