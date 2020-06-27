# PEBBLES Application

Table of Contents
==================
* [Modules Used](#modules-used)
* [Configuration Path](#configuration-path)

### Modules Used
```
--genweb2 modules
$ git clone -b pebbles-source --single-branch https://github.com/genweb2/gbs.git

--custom modules
$ git clone -b 8.0 --single-branch https://github.com/OCA/product-attribute.git
$ git clone -b 8.0 --single-branch https://github.com/OCA/server-tools.git
$ git clone -b 8.0 --single-branch https://github.com/OCA/web.git

--odoo modules
$ git clone -b 8.0 --single-branch https://github.com/odoo/odoo.git 8.0
```


### Configuration Path:

```
[options]
addons_path = /odoo/odoo-server/addons,/odoo/odoo-server/openerp/addons,/odoo/custom/addons/gbs,/odoo/custom/addons/product-attribute,/odoo/custom/server-tools,/odoo/custom/web
admin_passwd = <admin_password>
db_host = False
db_password = False
db_port = False
db_user = odoo
logfile = /var/log/odoo/odoo-server.log
xmlrpc_port = 9000
```

### Python packages

```
Babel==1.3
Jinja2==2.7.3
Mako==1.0.0
MarkupSafe==0.23
Pillow==2.5.1
Python-Chart==1.39
PyYAML==3.11
Werkzeug==0.9.6
argparse==1.2.1
decorator==3.4.0
docutils==0.12
feedparser==5.1.3
gdata==2.0.18
gevent==1.0.2
greenlet==0.4.7
jcconv==0.2.3
lxml==3.3.5
mock==1.0.1
passlib==1.6.2
psutil==2.1.1
psycogreen==1.0
psycopg2==2.7.1
pyPdf==1.13
pydot==1.0.2
pyparsing==1.5.7
pyserial==2.7
python-dateutil==1.5
python-openid==2.2.5
pytz==2014.4
pyusb==1.0.0b1
qrcode==5.0.1
reportlab==3.1.44
requests==2.6.0
simplejson==3.5.3
six==1.7.3
unittest2==0.5.1
vatnumber==1.2
vobject==0.6.6
wsgiref==0.1.2
xlwt==0.7.5
psycopg2-binary
```

