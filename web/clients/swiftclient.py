import object_storage
from django.conf import settings

sl_storage = object_storage.get_client(
    settings.SOFTLAYER_OS['username'],
    settings.SOFTLAYER_OS['api_key'],
    datacenter='sjc01')

sl_storage.containers()
# []

sl_storage['foo'].create()
# Container(foo)

sl_storage.containers()
# [Container(foo)]

sl_storage['foo'].properties
# {'count': 0, 'object_count': 0, 'name': 'foo', 'size': 0.0}

sl_storage['foo']['bar.txt'].create()
# StorageObject(foo, sample_object.txt)

sl_storage['foo']['bar.txt'].send('Plain-Text Content')
# True

sl_storage['foo']['bar.txt'].read()
# 'Plain-Text Content'

sl_storage['foo'].objects()
# [StorageObject(foo, bar.txt)]

sl_storage['foo']['bar.txt'].delete()
# True

sl_storage['foo'].delete()
# True