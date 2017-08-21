# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery import task
import requests
import json
from subprocess import Popen
from subprocess import PIPE


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
def submit_spark_job(job_id):
    req = requests.get("http://localhost:8000/jobs/" + job_id + "/", auth=("daniel", "welcome1111"))
    data = req.json()
    pipe = Popen(['/usr/local/spark/bin/spark-submit', '--master', 'yarn', '/home/spark/wordcount.py'], stdout=PIPE)
    stdout = pipe.communicate()[0].split("\n")
    for line in stdout:
	if "application_" in line:
	    print "hit the application id"
	    data['yarn_id'] = line 
	    print data
	    requests.put("http://localhost:8000/jobs/" + job_id + "/", data, auth=("daniel", "welcome1111"))
	    return
    
