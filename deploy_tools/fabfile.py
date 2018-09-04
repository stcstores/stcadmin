"""Fabfile."""

import posixpath
import random
import sys

from fabric.api import env, local, run
from fabric.context_managers import cd
from fabric.contrib.files import append, exists
from fabric.operations import sudo

env.shell = "/bin/bash -l -i -c"  # Use path from .bashrc

REPO_URL = "https://github.com/stcstores/stcadmin.git"


class Deploy:
    """Deploy site."""

    REPO_URL = REPO_URL
    VIRTUALENV = "virtualenv"
    SOURCE = "source"
    STATIC = "static"
    MEDIA = "media"

    def __init__(self, env):
        """Deploy site."""
        self.set_attributes(env)
        self.create_directory_structure()
        self.get_latest_source()
        self.update_settings()
        self.update_virtualenv()
        self.update_docs()
        self.update_static_files()
        self.update_database()
        self.restart_server()

    def set_attributes(self, env):
        """Set class atributes."""
        self.user = env.user
        self.host = env.host
        self.site_folder = posixpath.join("/home", env.user, "sites", env.host)
        self.source_folder = posixpath.join(self.site_folder, self.SOURCE)
        self.virtualenv_folder = posixpath.join(self.site_folder, self.VIRTUALENV)
        self.static_folder = posixpath.join(self.site_folder, self.STATIC)
        self.media_folder = posixpath.join(self.site_folder, self.MEDIA)
        self.log_folder = posixpath.join(self.site_folder, "logs")
        self.config_folder = posixpath.join(self.site_folder, "config")
        self.system_python = f"python{sys.version_info.major}.{sys.version_info.minor}"
        self.venv_python = posixpath.join(self.virtualenv_folder, "bin", "python")
        venv_activate_script = posixpath.join(self.virtualenv_folder, "bin", "activate")
        self.activate_virtual_env_command = f"source {venv_activate_script}"

    def venv_run(self, command):
        """Run command in virtual environment."""
        run(f"{self.activate_virtual_env_command} && {command}")

    def create_directory_structure(self):
        """Create necessary directories if necessary."""
        folders = [
            self.source_folder,
            self.virtualenv_folder,
            self.static_folder,
            self.media_folder,
            self.log_folder,
            self.config_folder,
        ]
        for subfolder in folders:
            run(f"mkdir -p {subfolder}")

    def get_latest_source(self):
        """Clone and/or update git repo."""
        if exists(posixpath.join(self.source_folder, ".git")):
            run(f"cd {self.source_folder} && git fetch")
        else:
            run("git clone {} {}".format(self.REPO_URL, self.source_folder))
        current_commit = local("git log -n 1 --format=%H", capture=True)
        run(f"cd {self.source_folder} && git reset --hard {current_commit}")

    def update_settings(self):
        """Configure settings.py and secret key."""
        secret_key_file = posixpath.join(self.config_folder, "secret_key.toml")
        if not exists(secret_key_file):
            chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$^&*"
            key = "".join([random.SystemRandom().choice(chars) for _ in range(50)])
            append(secret_key_file, f'SECRET_KEY = "{key}"')

    def update_virtualenv(self):
        """Create virtualenv and install packages."""
        run("rm -rf {}".format(self.virtualenv_folder))
        run(f"{self.system_python} -m venv {self.virtualenv_folder}")
        self.venv_run("pip install pip -U")
        self.venv_run("pip install pipenv --upgrade")
        with cd(self.source_folder):
            self.venv_run("pipenv install --ignore-pipfile")

    def update_docs(self):
        """Build documentation."""
        with cd(f"{self.source_folder}/reference/help"):
            self.venv_run("make html")

    def update_static_files(self):
        """Run collectstatic command."""
        with cd(self.source_folder):
            self.venv_run("python manage.py collectstatic --noinput")

    def update_database(self):
        """Run migrate command."""
        with cd(self.source_folder):
            self.venv_run("python manage.py migrate --noinput")

    def restart_server(self):
        """Restart server process."""
        sudo(f"systemctl restart gunicorn-{self.host}")


def deploy():
    """Deploy site."""
    Deploy(env)
