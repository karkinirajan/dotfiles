## All that you need to Know for putting Django app to production from scratch ;)

### Works on any vps based environment with linux

### I mean why would you pick other than Debian/Ubuntu :D

#### Prerequisites

## Create A Digital Ocean Droplet

This tutorial assumes that you have already set up your virtual private server (vps) with your operating system of choice (ubuntu will work just fine). If you have not already done so, you can follow this tutorial. Before you begin, make sure your cloud server is properly configured to host Django applications with a database server, web server, and virtualenv already installed. If you have not already done this, please follow steps 1 - 6 about setting up a server for Django.

#### Update Packages

Before doing anything, it is always good practice to ensure all of your packages managed through apt, or whatever your package manager of choice is, are up to date. You can do this by connecting to your VPS via SSH and running the following commands:

```
sudo apt-get update
```

```
sudo apt-get upgrade
```

The first command downloads any updates for packages managed through apt-get. The second command installs the updates that were downloaded. After running the above commands, if there are updates to install you will likely be prompted to indicate whether or not you want to install these updates. If this happens, just type “y” and then hit “enter” when prompted.
Step Two: Set Up Your Virtualenv

If you completed the prerequisites, this should already be set up and you can skip this step.

Now we need to set up our virtualenv where our project files and Python packages will live. If you don’t use virtualenv, then simply create the directory where your Django project will live and move to step three.

To create your virtualenv run the following command. Remember to replace the path with the desired path of your project project on the virtual private server:
first make sure you are at home directory then

```
cd mkdir myproject
```

```
python3 -m venv env
```

make sure venv is installed if not run the following command

```
sudo apt-get install python3-venv
```

Now that you have your virtualenv set up, you may activate your virtualenv and install Django and any other Python packages you may need using pip. Below is an example of how to activate your virtualenv and use pip to install Django:

#### In Linux, Mac

```
source env/bin/activate
```

#### In Windows

```
\env\Scripts\activate.bat
```

#### Install Django

```
pip install django
```

# Security & Access

### Creating SSH keys (Optional)

You can choose to create SSH keys to login if you want. If not, you will get the password sent to your email to login via SSH

To generate a key on your local machine

```
$ ssh-keygen
```

Hit enter all the way through and it will create a public and private key at

```
~/.ssh/id_rsa
~/.ssh/id_rsa.pub
```

You want to copy the public key (.pub file)

```
$ cat ~/.ssh/id_rsa.pub
```

Copy the entire output and add as an SSH key for Digital Ocean

### Login To Your Server

If you setup SSH keys correctly the command below will let you right in. If you did not use SSH keys, it will ask for a password. This is the one that was mailed to you

```
$ ssh root@YOUR_SERVER_IP
```

### Create a new user

It will ask for a password, use something secure. You can just hit enter through all the fields. I used the user "djangoadmin" but you can use anything

```
# adduser djangoadmin
```

### Give root privileges

```
# usermod -aG sudo djangoadmin
```

### SSH keys for the new user

Now we need to setup SSH keys for the new user. You will need to get them from your local machine

### Exit the server

You need to copy the key from your local machine so either exit or open a new terminal

```
# exit
```

You can generate a different key if you want but we will use the same one so lets output it, select it and copy it

```
$ cat ~/.ssh/id_rsa.pub
```

### Log back into the server

```
$ ssh root@YOUR_SERVER_IP
```

### Add SSH key for new user

Navigate to the new users home folder and create a file at '.ssh/authorized_keys' and paste in the key

```
# cd /home/djangoadmin
# mkdir .ssh
# cd .ssh
# nano authorized_keys
Paste the key and hit "ctrl-x", hit "y" to save and "enter" to exit
```

### Login as new user

You should now get let in as the new user

```
$ ssh djangoadmin@YOUR_SERVER_IP
```

### Disable root login

```
# sudo nano /etc/ssh/sshd_config
```

### Change the following

```
PermitRootLogin no
PasswordAuthentication no
```

### Reload sshd service

```
# sudo systemctl reload sshd
```

# Simple Firewall Setup

See which apps are registered with the firewall

```
# sudo ufw app list
```

Allow OpenSSH

```
### sudo ufw allow OpenSSH
```

### Enable firewall

```
# sudo ufw enable
```

### To check status

```
# sudo ufw status
```

We are now done with access and security and will move on to installing software

# Software

## Update packages

```
# sudo apt update
# sudo apt upgrade
```

## Install Python 3, Postgres & NGINX

```
# sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

# Postgres Database & User Setup

```
# sudo -u postgres psql
```

You should now be logged into the pg shell

### Create a database

```
CREATE DATABASE btre_prod;
```

### Create user

```
CREATE USER dbadmin WITH PASSWORD 'abc123!';
```

### Set default encoding, tansaction isolation scheme (Recommended from Django)

```
ALTER ROLE dbadmin SET client_encoding TO 'utf8';
ALTER ROLE dbadmin SET default_transaction_isolation TO 'read committed';
ALTER ROLE dbadmin SET timezone TO 'UTC';
```

### Give User access to database

```
GRANT ALL PRIVILEGES ON DATABASE btre_prod TO dbadmin;
```

### Quit out of Postgres

```
\q
```

# Vitrual Environment

You need to install the python3-venv package

```
# sudo apt install python3-venv
```

### Create project directory

```
# mkdir pyapps
# cd pyapps
```

### Create venv

```
# python3 -m venv ./venv
```

### Activate the environment

```
# source venv/bin/activate
```

# Git & Upload

### Pip dependencies

From your local machine, create a requirements.txt with your app dependencies. Make sure you push this to your repo

```
$ pip freeze > requirements.txt
```

Create a new repo and push to it (you guys know how to do that)

### Clone the project into the app folder on your server (Either HTTPS or setup SSH keys)

```
# git clone https://github.com/yourgithubname/btre_project.git
```

## Install pip modules from requirements

You could manually install each one as well

```
# pip install -r requirements.txt
```

# Local Settings Setup

Add code to your settings.py file and push to server

```
try:
    from .local_settings import *
except ImportError:
    pass
```

Create a file called **local_settings.py** on your server along side of settings.py and add the following

- SECRET_KEY
- ALLOWED_HOSTS
- DATABASES
- DEBUG
- EMAIL\_\*

## Run Migrations

```
# python manage.py makemigrations
# python manage.py migrate
```

## Create super user

```
# python manage.py createsuperuser
```

## Create static files

```
python manage.py collectstatic
```

### Create exception for port 8000

```
# sudo ufw allow 8000
```

## Run Server

```
# python manage.py runserver 0.0.0.0:8000
```

### Test the site at YOUR_SERVER_IP:8000

Add some data in the admin area

# Gunicorn Setup

Install gunicorn

```
# pip install gunicorn
```

Add to requirements.txt

```
# pip freeze > requirements.txt
```

### Test Gunicorn serve

```
# gunicorn --bind 0.0.0.0:8000 btre.wsgi
```

Your images, etc will be gone

### Stop server & deactivate virtual env

```
ctrl-c
# deactivate
```

### Open gunicorn.socket file

```
# sudo nano /etc/systemd/system/gunicorn.socket
```

### Copy this code, paste it in and save

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

### Open gunicorn.service file

```
# sudo nano /etc/systemd/system/gunicorn.service
```

### Copy this code, paste it in and save

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=djangoadmin
Group=www-data
WorkingDirectory=/home/djangoadmin/pyapps/btre_project
ExecStart=/home/djangoadmin/pyapps/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          btre.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Start and enable Gunicorn socket

```
# sudo systemctl start gunicorn.socket
# sudo systemctl enable gunicorn.socket
```

### Check status of guinicorn

```
# sudo systemctl status gunicorn.socket
```

### Check the existence of gunicorn.sock

```
# file /run/gunicorn.sock
```

# NGINX Setup

### Create project folder

```
# sudo nano /etc/nginx/sites-available/btre_project
```

### Copy this code and paste into the file

```
server {
    listen 80;
    server_name YOUR_IP_ADDRESS;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/djangoadmin/pyapps/btre_project;
    }

    location /media/ {
        root /home/djangoadmin/pyapps/btre_project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

### Enable the file by linking to the sites-enabled dir

```
# sudo ln -s /etc/nginx/sites-available/btre_project /etc/nginx/sites-enabled
```

### Test NGINX config

```
# sudo nginx -t
```

### Restart NGINX

```
# sudo systemctl restart nginx
```

### Remove port 8000 from firewall and open up our firewall to allow normal traffic on port 80

```
# sudo ufw delete allow 8000
# sudo ufw allow 'Nginx Full'
```

### You will probably need to up the max upload size to be able to create listings with images

Open up the nginx conf file

```
# sudo nano /etc/nginx/nginx.conf
```

### Add this to the http{} area

```
client_max_body_size 20M;
```

### Reload NGINX

```
# sudo systemctl restart nginx
```

### Media File Issue

You may have some issues with images not showing up. I would suggest, deleting all data and starting fresh as well as removeing the "photos" folder in the "media folder"

```
# sudo rm -rf media/photos
```

# Domain Setup

Go to your domain registrar and create the following a record

```
@  A Record  YOUR_IP_ADDRESS
www  CNAME  example.com
```

### Go to local_settings.py on the server and change "ALLOWED_HOSTS" to include the domain

```
ALLOWED_HOSTS = ['IP_ADDRESS', 'example.com', 'www.example.com']
```

### Edit /etc/nginx/sites-available/btre_project

```
server {
    listen: 80;
    server_name xxx.xxx.xxx.xxx example.com www.example.com;
}
```

### Reload NGINX & Gunicorn

```
# sudo systemctl restart nginx
# sudo systemctl restart gunicorn
```
