import object_storage
import json
import urllib2, base64

def index_object_store():
    sl_storage = object_storage.get_client(
        'SLOS1356065-2:SL1356065',
        'SL_API_KEY_HERE',
        datacenter='sjc01')

    containers = sl_storage.containers()
    for container in containers:
        url_data = 'http://localhost:8000/datasets/'
        req = urllib2.Request(url_data)
        base64string = base64.b64encode('%s:%s' % ('daniel', 'welcome1111'))
        req.add_header("Authorization", "Basic %s" % base64string)
        req.add_header('Content-Type', 'application/json')
        body = json.dumps({'name': container.name })
        urllib2.urlopen(req, body)

        objects = container.objects()
        for object in objects:
            url_raw = 'http://localhost:8000/raw/'
            location = str(object.url)
            if not (location.endswith(".fsa")):
                continue
            body = json.dumps({'dataset': container.name, 'location': str(object.url) })
            req = urllib2.Request(url_raw)
            req.add_header('Content-Type', 'application/json')
            urllib2.urlopen(req, body)

def create_queries():
    print "TODO"

def create_jobs():
    print "TODO"

if __name__ == "__main__":
    index_object_store()
