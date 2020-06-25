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

