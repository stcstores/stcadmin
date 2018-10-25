Provisioning a new site
=======================

## Required packages:

* nginx
* Python 3
* Git
* pip
* pipenv
* virtualenv

e.g.,, on Ubuntu:

    sudo apt-get install nginx git python3 python3-venv

## Install User Python

Do not use the system python. A user version of python can be installed using a get_python
script provided at https://gist.github.com/lukeshiner/dea6917e4d37ede1c1dae17fb993496d.
This takes the required python version as an argument.

Usage: ./get_python.sh 3.7.1

## Nginx Virtual Host config

* see nginx.template.conf
* replace SITENAME with, e.g., staging.my-domain.com
*   sed "s/SITENAME/<sitename>/g" \
    deploy_tools/nginx.template.conf | sudo tee \
    /etc/nginx/sites-available/<sitename>
* enable site by symlinking config file to /etc/nginx/sites-enabled

## Systemd service

* see gunicorn-systemd.template.service
* replace SITENAME with, e.g., staging.my-domain.com
* replace USERNAME with your username
*   sed "s/SITENAME/<sitename>/g; s/USERNAME/<username>" \
    deploy_tools/gunicorn-systemd.template.service | sudo tee \
    /etc/systemd/system/gunicorn-<sitename>.service

## Restart Services

* sudo systemctl daemon-reload
* sudo systemctl reload nginx
* sudo systemctl enable gunicorn-<sitename>
* sudo systemctl start gunicorn-<sitename>

## Get SSL Certificates

SSL certificates can be provided by Let's Encrypt, using certbot.

$ sudo apt-get update
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get update
$ sudo apt-get install python-certbot-nginx

sudo certbot certonly --webroot --webroot-path=/var/www/html -d example.co.uk \
-d www.example.co.uk
