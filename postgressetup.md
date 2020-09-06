### Postgres First Setup

####Do this first to check everything 
sudo su - postgres
initdb --locale en_US.UTF-8 -D /var/lib/postgres/data
exit
sudo systemctl start postgresql
sudo systemctl status postgresql


### and then do this for autoenabke on reboot


sudo systemctl enable postgresql
