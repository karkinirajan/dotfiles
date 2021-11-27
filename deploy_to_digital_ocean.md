## All That you need to Know for Putting Django app to production from scratch

#### Prerequisites

This tutorial assumes that you have already set up your virtual private server (vps) with your operating system of choice (ubuntu will work just fine). If you have not already done so, you can follow this tutorial. Before you begin, make sure your cloud server is properly configured to host Django applications with a database server, web server, and virtualenv already installed. If you have not already done this, please follow steps 1 - 6 about setting up a server for Django.

#### Step One: Update Packages

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

virtualenv /opt/myproject

Now that you have your virtualenv set up, you may activate your virtualenv and install Django and any other Python packages you may need using pip. Below is an example of how to activate your virtualenv and use pip to install Django:

source /opt/myproject/bin/activate

pip install django

Now we’re ready to create a database for our project!
Step Three: Create a Database

This tutorial assumes you use PostgreSQL as your database server. If not, you will need to check out documentation on how to create a database for your database server of choice.

To create a database with PostgreSQL start by running the following command:

sudo su - postgres

Your terminal prompt should now say “postgres@yourserver”. If so, run this command to create your database, making sure to replace “mydb” with your desired database name:

createdb mydb

Now create your database user with the following command:

createuser -P

You will now be met with a series of six prompts. The first will ask you for the name of the new user (use whatever name you would like). The next two prompts are for your password and confirmation of password for the new user. For the last three prompts, simply enter “n” and hit “enter.” This ensures your new user only has access to what you give it access to and nothing else. Now activate the PostgreSQL command line interface like so:

psql

Finally, grant this new user access to your new database with the following command:

GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;

You are now set with a database and a user to access that database. Next, we can work on configuring our web server to serve up our static files!
Step Four: Configure Your VPS

We need to create a new configuration file for our site. This tutorial assumes you are using NGINX as your cloud server. If this is not the case, you will need to check the documentation for your web server of choice in order to complete this step.

For NGINX, run the following command to create and edit your site’s web server configuration file, making sure to replace “myproject” at the end of the command with the name of your project:

sudo nano /etc/nginx/sites-available/myproject

Now enter the following lines of code into the open editor:

server {
server_name yourdomainorip.com;

    access_log off;

    location /static/ {
        alias /opt/myenv/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Real-IP $remote_addr;
        add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
    }

}

Save and exit the file. The above configuration has set NGINX to serve anything requested at yourdomainorip.com/static/ from the static directory we set for our Django project. Anything requested at yourdomainorip.com will proxy to localhost on port 8001, which is where we will tell Gunicorn (or your app server of choice) to run. The other lines ensure that the hostname and IP address of the request get passed on to Gunicorn. Without this, the IP address of every request becomes 127.0.0.1 and the hostname is just your VPS hostname.

Now we need to set up a symbolic link in the /etc/nginx/sites-enabled directory that points to this configuration file. That is how NGINX knows this site is active. Change directories to /etc/nginx/sites-enabled like this:

cd /etc/nginx/sites-enabled

Once there, run this command:

sudo ln -s ../sites-available/myproject

Now restart NGINX with the command below and you should be set:

sudo service nginx restart

You may see the following error upon restart:

server_names_hash, you should increase server_names_hash_bucket_size: 32

You can resolve this by editing ’ /etc/nginx/nginx.conf ’

Open the file and uncomment the following line:

server_names_hash_bucket_size 64;

Now let’s get our project files pushed up to our droplet!
Step Five: Move Local Django Project to Droplet

We have several options here: FTP, SFTP, SCP, Git, SVN, etc. We will go over using Git to transfer your local project files to your virtual private server.

Find the directory where you set up your virtualenv or where you want your project to live. Change into this directory with the following command:

cd /opt/myproject

Once there, create a new directory where your project files will live. You can do this with the following command:

mkdir myproject

It may seem redundant to have two directories with the same name; however, it makes it so that your virtualenv name and project name are the same.

Now change into the new directory with the following command:

cd myproject

If your project is already in a Git repo, simply make sure your code is all committed and pushed. You can check if this is the case by running the following command locally on your computer in a terminal (for Mac) or a command prompt (for PC):

git status

If you see no files in the output then you should be good to go. Now SSH to your droplet and install Git with the following command:

sudo apt-get install git

Make sure to answer yes to any prompts by entering “y” and hitting “enter.” Once Git is installed, use it to pull your project files into your project directory with the following command:

git clone https://webaddressforyourrepo.com/path/to/repo .

If you use Github or Bitbucket for Git hosting there is a clone button you can use to get this command. Be sure to add the “.” at the end. If we don’t do this, then Git will create a directory with the repo name inside your project directory, which you don’t want.

If you don’t use Git then use FTP or another transfer protocol to transfer your files to the project directory created in the steps above.

Now all that’s left is setting up your app server!
Step Six: Install and Configure App Server

If you completed the prerequisites, this should already be set up and you can skip this step.

Now we need to install our app server and make sure it listens on port 8001 for requests to our Django app. We will use Gunicorn in this example. To install Gunicorn, first activate your virtualenv:

source /opt/myproject/bin/activate

Once your virtualenv is active, run the following command to install Gunicorn:

pip install gunicorn

Now that Gunicorn is installed, bind requests for your domain or ip to port 8001:

gunicorn_django --bind yourdomainorip.com:8001

Now you can hit “ctrl + z” and then type “bg” to background the process (if you would like). More advanced configuration and setup of Gunicorn can be found in step nine of this tutorial.

Now you’re ready for the final step!
Step Seven: Configure Your App

The final step is to configure your app for production. All of the changes we need to make are in your “settings.py” file for your Django project. Open this file with the following command:

sudo nano /opt/myproject/myproject/settings.py

The path to your settings file may differ depending on how your project is set up. Modify the path in the command above accordingly.

With your settings file open, change the DEBUG settings to False:

DEBUG = False

This will make it so that errors will show up to users as 404 or 500 error pages, rather than giving them a stack trace with debug information.

Now edit your database settings to look like the following, using your database name, user, and password instead of the ones shown below:

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
'NAME': 'mydb', # Or path to database file if using sqlite3. # The following settings are not used with sqlite3:
'USER': 'myuser',
'PASSWORD': 'password',
'HOST': '', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
'PORT': '', # Set to empty string for default.
}
}

Now edit your static files settings:

STATIC_ROOT = '/opt/myproject/static/'

STATIC_URL = '/static/'

Save and exit the file. Now all we need to do is collect our static files. Change into the directory where your “manage.py” script is and run the following command:

python manage.py collectstatic

This command will collect all the static files into the directory we set in our settings.py file above.

And that’s it! You’ve now got your app deployed to production and ready to go.

#! Brad Part from here

# Django Deployment to Ubuntu 18.04

In this guide I will go through all the steps to create a VPS, secure it and deploy a Django application. This is a summarized document from this [digital ocean doc](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04)

Any commands with "$" at the beginning run on your local machine and any "#" run when logged into the server

## Create A Digital Ocean Droplet

Use [this link](https://m.do.co/c/5424d440c63a) and get $10 free. Just select the $5 plan unless this a production app.

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
