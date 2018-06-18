"""Fabfile."""

import os
import random

from fabric.api import env, local, put, run
from fabric.context_managers import cd
from fabric.contrib.files import append, exists, sed
from fabric.operations import sudo

env.shell = "/bin/bash -l -i -c"  # Use path from .bashrc

REPO_URL = 'https://github.com/stcstores/stcadmin.git'


class Deploy():
    """Deploy site."""

    REPO_URL = REPO_URL
    VIRTUALENV = 'virtualenv'
    SOURCE = 'source'
    STATIC = 'static'
    MEDIA = 'media'

    def __init__(self, env):
        """Deploy site."""
        self.set_attributes(env)
        self.create_directory_structure()
        self.get_latest_source()
        self.update_settings()
        self.add_server_settings()
        self.update_virtualenv()
        self.update_docs()
        self.update_static_files()
        self.update_database()
        self.restart_server()

    def set_attributes(self, env):
        """Set class atributes."""
        self.user = env.user
        self.host = env.host
        self.site_folder = '/home/{}/sites/{}/'.format(env.user, env.host)
        self.source_folder = '{}/{}'.format(self.site_folder, self.SOURCE)
        self.virtualenv_folder = '{}/{}'.format(
            self.site_folder, self.VIRTUALENV)
        self.static_folder = '{}/{}'.format(self.site_folder, self.STATIC)
        self.media_folder = '{}/{}'.format(self.site_folder, self.MEDIA)
        self.python_executable = '{}/bin/python'.format(self.virtualenv_folder)
        self.activate_virtual_env = 'source {}/bin/activate'.format(
            self.virtualenv_folder)

    def venv_run(self, command):
        """Run command in virtual environment."""
        run(
            'source {}/bin/activate && {}'.format(
                self.virtualenv_folder, command))

    def create_directory_structure(self):
        """Create necessary directories if necessary."""
        folders = [
            self.source_folder, self.virtualenv_folder, self.static_folder,
            self.media_folder
        ]
        for subfolder in folders:
            run('mkdir -p {}'.format(subfolder))

    def get_latest_source(self):
        """Clone and/or update git repo."""
        if exists(''.join([self.source_folder, '/.git'])):
            run('cd {} && git fetch'.format(self.source_folder))
        else:
            run('git clone {} {}'.format(self.REPO_URL, self.source_folder))
        current_commit = local("git log -n 1 --format=%H", capture=True)
        run(
            'cd {} && git reset --hard {}'.format(
                self.source_folder, current_commit))

    def update_settings(self):
        """Configure settings.py and secret key."""
        settings_path = self.source_folder + '/stcadmin/settings.py'
        sed(settings_path, "DEBUG = True", "DEBUG = False")
        sed(
            settings_path, 'ALLOWED_HOSTS =.+$',
            'ALLOWED_HOSTS = ["{}"]'.format(self.host))
        secret_key_file = self.source_folder + '/stcadmin/secret_key.py'
        if not exists(secret_key_file):
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!"@#$%^&*"'
            key = ''.join(
                [random.SystemRandom().choice(chars) for _ in range(50)])
            append(secret_key_file, "SECRET_KEY = '{}'".format(key, ))
        append(settings_path, '\nfrom . secret_key import SECRET_KEY')

    def add_server_settings(self):
        """Copy server settings file to server."""
        server_settings = '{}/stcadmin/local_settings.py'.format(
            self.source_folder)
        local_server_settings = os.path.join(
            os.path.dirname(__file__), 'server_settings.py')
        put(local_server_settings, server_settings)

    def update_virtualenv(self):
        """Create virtualenv and install packages."""
        if not exists('/'.join([self.virtualenv_folder, 'bin', 'pip'])):
            run('python -m venv {}'.format(self.virtualenv_folder))
        self.venv_run('pip install pip -U')
        self.venv_run('pip install pipenv --upgrade')
        with cd(self.source_folder):
            self.venv_run('pipenv install --ignore-pipfile')

    def update_docs(self):
        """Build documentation."""
        with cd('{}/reference/help'.format(self.source_folder)):
            self.venv_run('make html')

    def update_static_files(self):
        """Run collectstatic command."""
        with cd(self.source_folder):
            self.venv_run('python manage.py collectstatic --noinput')

    def update_database(self):
        """Run migrate command."""
        with cd(self.source_folder):
            self.venv_run('python manage.py migrate --noinput')

    def restart_server(self):
        """Restart server process."""
        sudo("systemctl restart gunicorn-{}".format(self.host))


def deploy():
    """Deploy site."""
    Deploy(env)
