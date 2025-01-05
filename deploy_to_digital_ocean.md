# Django Production Deployment Guide

A comprehensive guide for deploying Django applications to production on Linux-based VPS environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Server Setup](#initial-server-setup)
- [Security Configuration](#security-configuration)
- [Database Setup](#database-setup)
- [Application Deployment](#application-deployment)
- [Web Server Configuration](#web-server-configuration)
- [Domain Configuration](#domain-configuration)

## Prerequisites

- A VPS with Ubuntu/Debian
- A domain name (optional)
- Basic command line knowledge
- Your Django application code in a Git repository

## Initial Server Setup

1. Update system packages:

```bash
sudo apt update
sudo apt upgrade
```

2.Install required packages:

```bash
sudo apt install python3-pip python3-dev python3-venv \
    libpq-dev postgresql postgresql-contrib \
    nginx curl git
```

## Security Configuration

### Create Deploy User

```bash
# Create user and add to sudo group
sudo adduser djangoadmin
sudo usermod -aG sudo djangoadmin

# Set up SSH keys (recommended)
mkdir -p /home/djangoadmin/.ssh
echo "your-ssh-public-key" > /home/djangoadmin/.ssh/authorized_keys
chmod 700 /home/djangoadmin/.ssh
chmod 600 /home/djangoadmin/.ssh/authorized_keys
chown -R djangoadmin:djangoadmin /home/djangoadmin/.ssh
```

### Configure SSH

Edit `/etc/ssh/sshd_config`:

```bash
# Disable root login and password authentication
PermitRootLogin no
PasswordAuthentication no

# Restart SSH service
sudo systemctl reload sshd
```

### Configure Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Database Setup

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE your_db_name;
CREATE USER your_db_user WITH PASSWORD 'your_password';

# Configure user
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
```

## Application Deployment

### Set up Virtual Environment

```bash
# Create project directory
mkdir -p /home/djangoadmin/projects
cd /home/djangoadmin/projects

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate
```

### Deploy Application

```bash
# Clone repository
git clone your-repo-url

# Install dependencies
pip install -r requirements.txt

# Configure local settings
# Create local_settings.py with your production settings
```

### Initialize Application

```bash
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser
```

## Web Server Configuration

### Configure Gunicorn

Create `/etc/systemd/system/gunicorn.socket`:

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Create `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=djangoadmin
Group=www-data
WorkingDirectory=/home/djangoadmin/projects/your_project
ExecStart=/home/djangoadmin/projects/env/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          your_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Configure Nginx

Create `/etc/nginx/sites-available/your_project`:

```nginx
server {
    server_name example.com www.example.com;
    client_max_body_size 20M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    location /static/ {
        root /home/djangoadmin/projects/your_project;
    }

    location /media/ {
        root /home/djangoadmin/projects/your_project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

    listen 80;
}
```

### Enable and Start Services

```bash
# Enable and start Gunicorn
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/your_project /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## Domain Configuration

1. Configure DNS A records:
   - `@` → Your server IP
   - `www` → Your server IP

2. Update `ALLOWED_HOSTS` in your Django settings:

```python
ALLOWED_HOSTS = ['your-ip', 'example.com', 'www.example.com']
```

## Maintenance

- Regular system updates:

```bash
sudo apt update && sudo apt upgrade
```

- Monitor logs:

```bash
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u gunicorn
```

## Security Best Practices

1. Always use HTTPS in production
2. Regularly update dependencies
3. Use strong passwords and keep them secure
4. Regularly backup your database
5. Monitor server resources and logs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
