import os

from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, put
from fabric.operations import sudo
import random

REPO_URL = 'https://github.com/stcstores/stcadmin.git'


def deploy():
    site_folder = '/home/{}/sites/{}/'.format(env.user, env.host)
    source_folder = ''.join([site_folder, '/source'])
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _add_server_settings(source_folder)
    _update_virtualenv(source_folder)
    _update_docs(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)
    _restart_server(env.host)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('static', 'virtualenv', 'source'):
        run('mkdir -p {}/{}'.format(site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(''.join([source_folder, '/.git'])):
        run('cd {} && git fetch'.format(source_folder))
    else:
        run('git clone {} {}'.format(REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd {} && git reset --hard {}'.format(source_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/stcadmin/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(
        settings_path, 'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["{}"]'.format(site_name))
    secret_key_file = source_folder + '/stcadmin/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!"@#$%^&*"'
        key = ''.join([random.SystemRandom().choice(chars) for _ in range(50)])
        append(secret_key_file, "SECRET_KEY = '{}'".format(key,))
    append(settings_path, '\nfrom . secret_key import SECRET_KEY')


def _add_server_settings(source_folder):
    server_settings_file = source_folder + '/stcadmin/local_settings.py'
    local_server_settings_file = os.path.join(
        os.path.dirname(__file__), 'server_settings.py')
    put(local_server_settings_file, server_settings_file)


def _update_virtualenv(source_folder):
    virtualenv_folder = '/'.join([source_folder, '..', 'virtualenv'])
    if not exists('/'.join([virtualenv_folder, 'bin', 'pip'])):
        run('python3 -m venv {}'.format(virtualenv_folder))
    run('{}/bin/pip install -U -r {}/requirements.txt'.format(
        virtualenv_folder, source_folder))


def _update_docs(source_folder):
    run('cd {}/docs && make html')


def _update_static_files(source_folder):
    run(
        'cd {} && ../virtualenv/bin/python manage.py collectstatic \
        --noinput'.format(source_folder))


def _update_database(source_folder):
    run(
        'cd {} && ../virtualenv/bin/python manage.py migrate \
        --noinput'.format(source_folder))


def _restart_server(project_name):
    sudo("systemctl restart gunicorn-{}".format(project_name))
