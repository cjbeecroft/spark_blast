import object_storage
import json
import urllib2, base64

def destroy_object_index():
    url_data = 'http://localhost:8000/datasets/'
    req = urllib2.Request(url_data)
    base64string = base64.b64encode('%s:%s' % ('daniel', 'welcome1111'))
    req.add_header("Authorization", "Basic %s" % base64string)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req)
    body = json.loads(response.read())
    print body
    for i in body:
        name = i['name']
        print name
        delete_url= "http://localhost:8000/datasets/%s/" % (name)
        req = urllib2.Request(delete_url)
        base64string = base64.b64encode('%s:%s' % ('daniel', 'welcome1111'))
        req.add_header("Authorization", "Basic %s" % base64string)
        req.get_method = lambda: 'DELETE'
        response = urllib2.urlopen(req)






if __name__ == "__main__":
    destroy_object_index()