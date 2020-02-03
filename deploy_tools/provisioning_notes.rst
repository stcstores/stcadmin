Provisioning a new site
***********************

Required packages:
##################
* :code:`nginx`
* :code:`Python 3`
* :code:`Git`
* :code:`pip`
* :code:`poetry`
* :code:`postgres`
* :code:`webhook`

Install User Python
###################

Do not use the system python. A user version of python can be installed using
the get_python script provided at
https://gist.github.com/lukeshiner/dea6917e4d37ede1c1dae17fb993496d.

This takes the required python version as an argument::

    ./get_python.sh 3.8.1

Install poetry::

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

Create Site Directory
#####################

Create the following directory structure:
::

| $HOME
| ├── sites
| |    ├── <sitename>
| |    |    ├── config
| |    |    ├── logs
| |    |    ├── media
| |    |    ├── scripts
| |    |    ├── static

Clone the repo into :code:`/home/<username>/sites/<sitename>/source` and
checkout the desired ref.

Copy scripts to the scripts directory:

.. code-block:: bash

    cd ~/sites/<sitename>
    cp source/deploy_tools/scripts/env.sh scripts/
    cp source/deploy_tools/scripts/restart.sh scripts/
    cp source/deploy_tools/scripts/start.sh scripts/
    cp source/deploy_tools/scripts/update.sh scripts/

Add :code:`config.toml` and :code:`secret_key.toml` to the :code:`config`
directory.

Nginx Virtual Host config
#########################

Replace SITENAME in `nginx.template.conf` and copy to
:code:`/etc/nginx/sites-available/<sitename>`:

.. code-block:: bash

    sed "s/SITENAME/<sitename>/g" deploy_tools/nginx.template.conf | sudo tee /etc/nginx/sites-available/<sitename>

Enable site by symlinking config file to :code:`/etc/nginx/sites-enabled`:

.. code-block:: bash

    sudo ln -s /etc/nginx/sites-available/<sitename> /etc/nginx/sites-enabled/<sitename>

Systemd service
###############

Install the service config file, replacing the username and sitename,
then enable and start the service:

.. code-block:: bash

    sed "s/SITENAME/<sitename>/g; s/USERNAME/<username>/g" deploy_tools/gunicorn-systemd.template.service | sudo tee etc/systemd/system/gunicorn-<sitename>.service
    sudo systemctl enable gunicorn-<sitename>.service
    sudo systemctl start gunicorn-<sitename>.service

Get SSL Certificates
####################

SSL certificates can be provided by Let's Encrypt, using certbot:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install software-properties-common
    sudo add-apt-repository ppa:certbot/certbot
    sudo apt-get update
    sudo apt-get install python-certbot-nginx
    sudo certbot certonly --webroot --webroot-path=/var/www/html -d example.co.uk -d www.example.co.uk

Setup Webook
############
Install webhook:

.. code-block:: bash

  go get github.com/adnanh/webhook

Create a new webook in github in the settings for the repository

* Payload: [DOMAIN]:9000/hooks/stcadmin-github-push
* Content Type: application/json
* Secret: A random string
* Just push the event

Replace SECRET in hooks.json with the secret string and save
as :code:`/var/webhook/hooks.json`.

Copy :code:`stcadmin-github-push.sh` to
:code:`/var/webhook/scripts/stcadmin-github-push.sh`.

Replace USERNAME in webhook.service and save
as :code:`/etc/systemd/system/webhook.service`.

Restart services:

.. code:: bash

    sudo systemctl deamon-reload
    sudo systemctl enable webhook
    sudo systemctl start webhook

Setup Database Backup
#####################

Instructions for server backups can be found at
https://gist.github.com/lukeshiner/e2b52786f40562bf7e334332012352d2
