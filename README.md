# [gbs]
## Genweb2 ERP Based Business Solution

### Repositiory which are need to run Samdua ERP

1. Clone odoo version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://www.github.com/odoo/odoo.git ```<br/>

2. Clone genweb2 GBS version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/genweb2/gbs.git ```<br/>

3. Clone custom repository for Operating Unit version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/OCA/operating-unit.git ```<br/>

4. Clone custom repository for HR version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/OCA/hr.git ```<br/>

5. Clone custom repository for WEB version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/OCA/web.git ```<br/>

6. Clone custom repository for Server Tools version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/OCA/server-tools.git ```<br/>

7. Clone custom repository for Odoo Community Addons version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://bitbucket.org/matiarrahman/odoo-community-addons.git ```<br/>

8. Clone custom repository for Sale Workflow version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/OCA/sale-workflow.git ```<br/>

9. Clone custom repository for Purchase Workflow version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/OCA/purchase-workflow.git ```<br/>

10. Clone custom repository for Partner Contact version 10.0
<br/>```$ git clone -b 10.0 --single-branch https://github.com/OCA/partner-contact.git ```<br/>

### Install software which are needed for device configuation

```$ sudo su```<br />
```$ curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -```<br />
```$ curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql.list```<br />
```$ exit```<br />
```$ sudo apt-get update```<br />
```$ sudo apt-get python-dev```<br />
```$ sudo apt-get install msodbcsql mssql-tools unixodbc-dev```<br />
```$ sudo pip install pyodbc```<br />

<strong>Note:</strong> https://docs.microsoft.com/en-us/azure/sql-database/sql-database-connect-query-python

### Install python package for reporting

```$sudo pip install xlsxwriter```<br />
