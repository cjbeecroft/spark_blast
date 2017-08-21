#!/usr/bin/env python
from deployer.client import start
from deployer.node import Node
from deployer.utils import esc1
import os

class DjangoDeployment(Node):
    project_directory = '~/git/django-project'
    repository = 'git@github.com:example/example.git'

    def install_git(self):
        """ Installs the ``git`` package. """
        self.host.sudo('apt-get install git')

    def git_clone(self):
        """ Clone repository."""
        with self.host.cd(self.project_directory, expand=True):
            self.host.run("git clone '%s'" % esc1(self.repository))

    def git_checkout(self, commit):
        """ Checkout specific commit (after cloning)."""
        with self.host.cd(self.project_directory, expand=True):
            self.host.run("git checkout '%s'" % esc1(commit))

from deployer.host import SSHHost

class remote_host(SSHHost):
    address = '158.85.15.58' # Replace by your IP address
    username = 'spark'
    key_filename = "/home/dbalck"# Optional, specify the location of the RSA
                            #   private key