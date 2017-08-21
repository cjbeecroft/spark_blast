# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from subprocess import call

class WebappConfig(AppConfig):
    name = 'webapp'
    def ready(self):
        call(['redis-server', '--daemonize', 'yes'])
        #call(['celery', '-A', 'webapp', 'worker', '-l', 'info'])

