from subprocess import Popen
from subprocess import PIPE
import requests

class CLInterface():
    def __init__(self):
        print("noop")

    def submit_job(self, instance):

        with open('/data/test/test.log', 'w') as f:
            #process = Popen(your_command, stdout=subprocess.PIPE)
            pipe = Popen(['/usr/local/spark/bin/spark-submit', '--master', 'yarn', '/home/spark/wordcount.py'], stderr=PIPE)
            for c in iter(lambda: pipe.communicate()[1], ''):
                if "applicationId" in c:
                    requests.put("http://localhost:8000/jobs/" + instance.job_id)
		    break
            pipe.terminate()




    def poll_job(self, yarn_id):
        pipe = Popen('yarn application -appId ' + yarn_id, stderr=PIPE)




