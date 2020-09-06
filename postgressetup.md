# Postgres First Setup

## Do this first to check everything 
</br>
$ sudo su - postgres
</br>
$ initdb --locale en_US.UTF-8 -D /var/lib/postgres/data
</br>
$ exit
</br>
$ sudo systemctl start postgresql
</br>
$ sudo systemctl status postgresql

##  And do this to enable on reboot
</br>
$ sudo systemctl enable postgresql
