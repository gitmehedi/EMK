# EMK Project
## Genweb2 ERP Based Business Solution

### Repository needed to run EMK Project
```
$ git clone -b 10.0 --single-branch https://github.com/OCA/server-tools.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/web.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/hr.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/event.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/reporting-engine.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/contract.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/vertical-association.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/partner-contact.git
$ git clone -b 10.0 --single-branch https://github.com/thinkopensolutions/tko-addons.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/operating-unit.git
$ git clone -b oca --single-branch https://github.com/genweb2/gbs.git
$ git clone -b emk --single-branch https://github.com/genweb2/gbs.git
```


### Install software which are needed for device configuration

```
$ sudo su
$ curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
$ curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql.list
$ exit
$ sudo apt-get update
$ sudo apt-get python-dev
$ sudo apt-get install msodbcsql mssql-tools unixodbc-dev
$ sudo pip install pyodbc
```

<strong>Note:</strong> https://docs.microsoft.com/en-us/azure/sql-database/sql-database-connect-query-python

### Install python package for reporting

```
$ sudo pip install xlsxwriter
```
