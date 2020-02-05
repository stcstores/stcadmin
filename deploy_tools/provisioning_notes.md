# Provisioning a new site

## Required packages:
* `nginx`
* `Git`
* `Python 3`
* `pip`
* `poetry`
* `postgres`
* `webhook`
* `certbot`

## Install User Python

Do not use the system python. A user version of python can be installed using
the get_python script provided at
https://gist.github.com/lukeshiner/dea6917e4d37ede1c1dae17fb993496d.

This takes the required python version as an argument:

```bash
$ ./get_python.sh 3.8.1
```

Install poetry:

```bash
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

## Create Site Directory

Create the following directory structure:

```
$HOME
├── sites
|    ├── <sitename>
|    |    ├── config
|    |    ├── logs
|    |    ├── media
|    |    ├── scripts
|    |    ├── static
```

Clone the repo into `/home/<username>/sites/<sitename>/source` and checkout the desired ref.

Copy scripts to the scripts directory:

```bash
$ cd ~/sites/<sitename>
$ cp source/deploy_tools/scripts/env.sh scripts/
$ cp source/deploy_tools/scripts/restart.sh scripts/
$ cp source/deploy_tools/scripts/start.sh scripts/
$ cp source/deploy_tools/scripts/update.sh scripts/
```

Add `config.toml` and `secret_key.toml` to the `config` directory.

## Nginx Virtual Host config

Replace SITENAME in `nginx.template.conf` and copy to
`/etc/nginx/sites-available/<sitename>`:

```bash
$ sed "s/SITENAME/<sitename>/g" deploy_tools/nginx.template.conf | sudo tee \ 
/etc/nginx/sites-available/<sitename>
```

Enable site by symlinking config file to `/etc/nginx/sites-enabled`:

```bash
$ sudo ln -s /etc/nginx/sites-available/<sitename> /etc/nginx/sites-enabled/<sitename>
```

## Systemd service

Install the service config file, replacing the username and sitename, then enable and start the service:

```bash
$ sed "s/SITENAME/<sitename>/g; s/USERNAME/<username>/g" deploy_tools/gunicorn-systemd.template.service \ |sudo tee etc/systemd/system/gunicorn-<sitename>.service
$ sudo systemctl enable gunicorn-<sitename>.service
$ sudo systemctl start gunicorn-<sitename>.service
```

## Get SSL Certificates

SSL certificates can be provided by Let's Encrypt, using certbot:

```bash
$ sudo apt-get update
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get update
$ sudo apt-get install python-certbot-nginx
$ sudo certbot certonly --webroot --webroot-path=/var/www/html -d example.co.uk \
-d www.example.co.uk
```

## Setup Webook

Install webhook:

```bash
$ go get github.com/adnanh/webhook
```

* Create a new webook in github in the settings for the repository

  *  Payload: [DOMAIN]:9000/hooks/stcadmin-github-push
  * Content Type: application/json
  * Secret: A random string
  * Just push the event

* Replace SECRET in hooks.json with the secret string and save as `/var/webhook/hooks.json`.
* Copy `stcadmin-github-push.sh` to `/var/webhook/scripts/stcadmin-github-push.sh`.
* Replace `USERNAME` in webhook.service and save as `/etc/systemd/system/webhook.service`.

Restart services:

```bash
$ sudo systemctl deamon-reload
$ sudo systemctl enable webhook
$ sudo systemctl start webhook
```

## Setup Database Backup

Instructions for server backups can be found at
https://gist.github.com/lukeshiner/e2b52786f40562bf7e334332012352d2
