# GET Protocol community site readme
This readme provides the installation instruction how to install this site in a production or development environment.

This readme supports the following two environments: (Other distro's environments work, but you have to translate the readme to your own environment.)
* Production: Debian based server, Apache server, MariaDB database, HTTPS with Let's encrypt certificate
* Development: Python webserver, SQLLite DB, HTTP

## Production environment
The following steps can be followed to install the site in a production environment.

### Install OS requirements
Install Apache, mod-wsgi for Python 3, let's encrypt module, Maria DB, Python virtual environment, GIT
```
sudo apt-get update
sudo apt-get install libapache2-mod-wsgi-py3 mariadb-server libmariadbclient-dev  python-certbot-apache python3-venv git gcc python-dev default-libmysqlclient-dev python3-dev
```

### Configure MariaDB
Run the following command to secure the MariaDB installation. Press enter for the current root password. Swap %ROOTPASSWORD% with a password for the root
```
sudo mysql_secure_installation
Enter current password for root (enter for none):
Set root password? [Y/n] y
New password: %ROOTPASSWORD%
Re-enter new password: %ROOTPASSWORD%
Remove anonymous users? [Y/n] y
Disallow root login remotely? [Y/n] y
Remove test database and access to it? [Y/n] y
Reload privilege tables now? [Y/n] y
```
Create a database. Replace '%DATABASEPASSWORD% for a database password
```
sudo mysql -u root -p
Enter password: %ROOTPASSWORD
CREATE DATABASE getsite;
CREATE USER 'getsiteuser'@'localhost' IDENTIFIED BY '%DATABASEPASSWORD%';
GRANT ALL PRIVILEGES ON getsite.* TO 'getsiteuser'@'localhost';
quit
```

### Enable HTTPS on the apache site
This readme will use the default Apache site. Changes the corresponding config files if you want to use another apache site.
Add 'ServerName get.powerplatz.nl' to /etc/apache2/sites-available/000-default.conf

User Certbot to request an Let's Encrypt Certificate
```
sudo certbot --apache -d get.powerplatz.nl
Enter email address (used for urgent renewal and security notices) (Enter 'c' tocancel): your@mail.example
Term of agreements: (A)gree/(C)ancel: A
Share e-mail (Y)es/(N)o: n
Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
```

### Create environment variabeles file
Add the following content to: /etc/getsite/environ.py
```
import os
os.environ['getsite_secret_key'] = '%DJANGOSECRETKEY%'
os.environ['getsite_debug'] = 'False'
os.environ['getsite_etherscan_apikey'] = '%ETHERSCANAPIKEY%'
os.environ['getsite_environment'] = 'Production'
os.environ['getsite_dbpassword'] = '%DATABASEPASSWORD%'
```

Replace %DJANGOSECRETKEY% with a Django secret key. This one can be generated with the following command:
```
python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]))'
```
Replace %ETHERSCANAPIKEY% with an API key which you can generate when you create an account on etherscan.io

Replace %DATABASEPASSWORD% with the database password created earlier

### Adjust Apache site
Add the following snippet to the Apache site /etc/apache2/sites-available/000-default-le-ssl.conf

```
<IfModule mod_ssl.c>
<VirtualHost *:443>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        ServerName get.powerplatz.nl

        ServerAdmin deofex@getprotocoltelegram

        Alias /static /var/www/getsite/static/
        WSGIScriptAlias / /var/www/getsite/getsite/wsgi.py

        WSGIDaemonProcess get.powerplatz.nl python-home=/usr/local/venv/getsite python-path=/var/www/getsite
        WSGIProcessGroup get.powerplatz.nl

        <Directory /var/www/getsite/static>
            Require all granted
        </Directory>
        <Directory /var/www/getsite>
            <Files wsgi.py>
                Require all granted
            </Files>
        </Directory>

        DocumentRoot /var/www/getsite
```
Leave the content below the DocumentRoot row untouched

### Create log folder
Create the folder where the log files will be places in
```
sudo mkdir /var/log/getsite
sudo chown %WEBADMINUSER% -R /var/log/getsite/
```
### Create the folder which contain the site
Create the 'getsite' folder in /var/www and give ownership to the user
```
sudo mkdir /var/www/getsite
sudo chown %WEBADMINUSER% -R /var/www/getsite
```


### Clone the github repository
git clone https://github.com/Deofex/GETStateChange.git /var/www/getsite

### Create the Python virtual environment
Create a Python vitual environment with the following commands (first create a root folder, than create the virtual environment)
```
sudo mkdir /usr/local/venv
sudo python3 -m venv /usr/local/venv/getsite
```

Activate the virtual environment
```
source /usr/local/venv/getsite/bin/activate
```

### Download modules
Upgrade PIP in the virtual environment
```
sudo sh -c ". /usr/local/venv/getsite/bin/activate ; pip install --upgrade pip"
```

Install requirements
```
sudo sh -c ". /usr/local/venv/getsite/bin/activate ; pip install -r /var/www/getsite/requirements.txt"
```

Restart Apache
```
sudo service apache2 restart
```

### Import environment variabels
Import the environment variables in the shell, so we can use the management.py script
```
export getsite_secret_key='%DJANGOSECRETKEY%'
export getsite_debug='False'
export getsite_etherscan_apikey '%ETHERSCANAPIKEY%'
export getsite_environment='Production'
export getsite_dbpassword='%DATABASEPASSWORD%'
```


### Create DB structure
```
python /var/www/getsite/manage.py migrate
```

### Collect Static files
```
python /var/www/getsite/manage.py collectstatic
```

### Create Cronjob to import new transactions
Create /etc/getsite/cron_importtransactions.sh with the following content
```
source /usr/local/venv/getsite/bin/activate

export getsite_secret_key='%DJANGOSECRETKEY%'
export getsite_debug='False'
export getsite_etherscan_apikey='%ETHERSCANAPIKEY%'
export getsite_environment='Production'
export getsite_dbpassword='%DATABASEPASSWORD%'


/var/www/getsite/manage.py importstatechanges
```

Provide 'run' permissions to the file

Add the following to the crontab, to make it run once a hour (5 minutes past the hour)
```
5 */1 * * * /usr/bin/env bash -c '/etc/getsite/cron_importtransactions.sh' > /tmp/cron_importtransactions.log 2>&1
```

### Create Cronjob to import the crypto prices
Create /etc/getsite/cron_importprice.sh with the following content
```
source /usr/local/venv/getsite/bin/activate

export getsite_secret_key='%DJANGOSECRETKEY%'
export getsite_debug='False'
export getsite_etherscan_apikey='%ETHERSCANAPIKEY%'
export getsite_environment='Production'
export getsite_dbpassword='%DATABASEPASSWORD%'


/var/www/getsite/manage.py importprices
```

Provide 'run' permissions to the file

Add the following to the crontab, to make it run once a hour (Every 5 minutes)
```
*/5 * * * * /usr/bin/env bash -c '/etc/getsite/cron_importprice.sh' > /tmp/cron_importprice.log 2>&1
```

### Create Cronjob to create the GET month statistics
Create /etc/getsite/cron_importburntransactions.sh with the following content
```
source /usr/local/venv/getsite/bin/activate

export getsite_secret_key='%DJANGOSECRETKEY%'
export getsite_debug='False'
export getsite_etherscan_apikey='%ETHERSCANAPIKEY%'
export getsite_environment='Production'
export getsite_dbpassword='%DATABASEPASSWORD%'


/var/www/getsite/manage.py importburntransactions
```

Provide 'run' permissions to the file

Add the following to the crontab, to make it run once a hour (10 minutes past the hour)
```
10 */1 * * * /usr/bin/env bash -c '/etc/getsite/cron_importburntransactions.sh' > /tmp/cron_importburntransactions.log 2>&1
```



## Development environment
More detailed steps will follow, but in short:

* Clone Git
* Add development ip/hostname in ALLOWED_HOSTS
* Create virtual environment
* pip install --upgrade pip
* pip install -r requirements.txt
* Add variabels
```
export getsite_secret_key='%DJANGOSECRETKEY%'
export getsite_debug='True'
export getsite_etherscan_apikey='%ETHERSCANAPIKEY%'
export getsite_environment='Development'
```

* Create database objects
```
python /var/www/getsite/manage.py migrate
```
* run server
```
python /var/www/getsite/manage.py runserver 0.0.0.0:8000
```
* Add development ip/hostname in ALLOWED_HOSTS