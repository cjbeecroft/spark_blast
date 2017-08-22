import object_storage
import json
import requests
import os

def index_object_store():
    sl_storage = object_storage.get_client(
        'SLOS1356065-2:SL1356065',
        os.environ['SL_API_KEY'],
        datacenter='sjc01')

    containers = sl_storage.containers()
    auth = ('daniel', 'welcome1111')
    for container in containers:
        datasets_url = 'http://localhost:8000/datasets/'
        headers = {'Content-Type': 'application/json'}
        body = json.dumps({'name': str(container.name)})
        print datasets_url
        print body
        print headers
        r = requests.post(datasets_url, data=body, headers=headers, auth=auth)
        print r
        objects = container.objects()
        for object in objects:
            raw_url = 'http://localhost:8000/raw/'
            location = str(object.url)
            if not (location.endswith(".fsa")):
                continue
            body = json.dumps({'dataset': container.name, 'location': str(location)})
            headers = {'Content-Type': 'application/json'}
            requests.post(raw_url, data=body, headers=headers, auth=auth)

def create_queries():
    print "TODO"

def create_jobs():
    print "TODO"

if __name__ == "__main__":
    index_object_store()
