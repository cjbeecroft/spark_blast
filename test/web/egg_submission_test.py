from sjsclient import client
from sjsclient import app as sjsapp
import requests

class SubmitEgg:

    def submit(self, url):


        sjs = client.Client(url)
        egg_file_path = "/home/dbalck/251/spark_blast/test/spark/dist/blast-0.0.0-py2.7.egg"
        egg_blob = open(egg_file_path, 'rb').read()
        wc_app = sjs.apps.create("ttc_wordcount", egg_blob, sjsapp.AppType.PYTHON)
        for app in sjs.apps.list():
            print app.name

        test_app = sjs.apps.get("ttc_wordcount")
        class_path = "spark.wordcount.WordCountSparkJob"
        # config = {"test_config": "test_config_value"}
        job = sjs.jobs.create(test_app, class_path)
        print("Job Status: ", job.status)

        # response = requests.delete(url + "/binaries/ttc_wordcount")

if __name__ == "__main__":
    se = SubmitEgg()
    se.submit("http://158.85.15.58:8090")