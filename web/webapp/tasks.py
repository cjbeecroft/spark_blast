# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import task
import requests
import os
import json
from subprocess import Popen
from subprocess import call
from subprocess import PIPE

@task(name="download_data")
def download_data(job_id):
    job = requests.get("http://localhost:8000/jobs/" + job_id + "/", auth=("daniel", "welcome1111"))
    print "got job!"
    datasets = job.json()['datasets']
    all_files = []
    config_str = "--conf " + "dirs="
    for dataset in datasets:
        print "iterating in datasets"
        data = requests.get(dataset, auth=("daniel", "welcome1111")).json()

        # if the hdfs_dir field is empty, it isn't on hdfs. we download and copy it there
        if (data['hdfs_dir'] == None | data['hdfs_dir'] == ''| data['hdfs_dir'] == 'null'):
            hdfs_files = []
            id = data['name']
            path = "/data/spark_blast/" + id
            call(['mkdir', '-p', path]) # make local dir for downloading
            call(['hdfs', 'dfs', '-mkdir', '-p', path]) # make hdfs dir for uploading and sharing among nodes

            # copy all files from object store to hdfs
            for url in data['raw_data']:
                filename = url.split('/')[-1]
                r = requests.get(url, stream=True)
                with open(os.path.join(path, filename), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                # move to hdfs
                call(['hdfs', 'dfs', '-moveFromLocal', os.path.join(path, filename), os.path.join(path, filename)])
                hdfs_files.append(os.path.join(path, filename))
            data['hdfs_dir'] = path
            requests.put(data['location'], json.dumps(data), auth=("daniel", "welcome1111"))

        config_str.append(data['hdfs_dir'] + ",")
        config_str = config_str[:-1]
    print config_str


@task(name="submit_spark_job")
def submit_spark_job(job_id):
    job = requests.get("http://localhost:8000/jobs/" + job_id + "/", auth=("daniel", "welcome1111"))

    pipe = Popen(['/usr/local/spark/bin/spark-submit', '--master', 'yarn', '/home/spark/wordcount.py'], stdout=PIPE)
    stdout = pipe.communicate()[0].split("\n")
    for line in stdout:
	if "application_" in line:
	    print "hit the application id"
	    job['yarn_id'] = line
	    print job
	    requests.put("http://localhost:8000/jobs/" + job_id + "/", data, auth=("daniel", "welcome1111"))
	    return
    
