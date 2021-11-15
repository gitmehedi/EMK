# Genweb2 Business Solution [GBS]
Table of Contents
=================

- [Genweb2 Business Solution [GBS]](#genweb2-business-solution-gbs)
- [Table of Contents](#table-of-contents)
  - [Application Architecture](#application-architecture)
    - [Three Tier Server Installation:](#three-tier-server-installation)
      - [1. Client/Web Server:](#1-clientweb-server)
      - [2. Application Server:](#2-application-server)
      - [3. Database Server:](#3-database-server)
  - [Source Repository](#source-repository)
      - [Base Odoo Source](#base-odoo-source)
      - [Community Source](#community-source)
      - [Application Source](#application-source)
  - [Database Clean Query](#database-clean-query)


## Application Architecture

In 3-tier architecture, there is an intermediary level, meaning that the architecture is generally split up between: 
1. **The Client or Web server**, i.e. the computer, which requests the resources, equipped with a user interface 
(usually a web browser) for presentation purposes; 
2. **The Application Server** (also called middleware), whose task it is to provide the requested resources, but by calling on another server.
3. **The Data Server**, which provides the application server with the data that it requires: 


### Three Tier Server Installation:

#### 1. Client/Web Server:

**Step 1:** Update OS and Install nginx web server

_Update OS_  
```sh
$ sudo yum update -y
```
_Donwload nginx and install in Redhat 7_ 
```sh
$ wget http://nginx.org/packages/rhel/7/x86_64/RPMS/nginx-1.14.2-1.el7_4.ngx.x86_64.rpm
$ sudo yum install nginx-1.14.2-1.el7_4.ngx.x86_64.rpm -y 
```

**Step 2:** Configure nginx with OS  

_Create symbolic link for nginx_
```sh
$ sudo systemctl enable nginx
```
**_Start of nginx_** 
```sh
$ sudo systemctl start nginx
```
**_Stop of nginx_** 
```sh
$ sudo systemctl stop nginx
```
**_Retart of nginx_** 
```sh
$ sudo systemctl restart nginx
```
**_Status of nginx_** 
```sh
$ sudo systemctl status nginx
```
**Step 3:** Additional configuration of nginx  

**_Open 80 and 443 port using firewall-cmd_**  
Install ```firewalld``` OS package with configuration in redhat.  
```sh
$ sudo yum install firewalld -y
$ sudo systemctl enable firewalld
$ sudo systemctl start firewalld
```
You must open and enable port 80 and 443 using the firewall-cmd command:
```sh
$ sudo firewall-cmd --permanent --zone=public --add-service=http
$ sudo firewall-cmd --permanent --zone=public --add-service=https
$ sudo firewall-cmd --reload
```
**Step 5:** Testing nginx configuration
```sh
$ sudo ss -tulpn
```

**Step 6:** Configure nginx server

Create a default configuration file in nginx folder /etc/nginx/conf.d/default.conf
Content of file.
```sh
server {
         listen 80;
         server_name appserver.com;
         client_max_body_size 4096M;
         proxy_read_timeout 720s;
         proxy_connect_timeout 720s;
         proxy_send_timeout 720s;

         # Add Headers for odoo proxy mode
         proxy_set_header X-Forwarded-Host $host;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto $scheme;
         proxy_set_header X-Real-IP $remote_addr;
         
         location / {
            proxy_set_header Host $host;
            proxy_pass "http://IP_ADDRESS:8010";
         }
         location /longpolling {
            proxy_pass "http://IP_ADDRESS:8072";
         }
}
```
**_Note_**: Change IP(192.168.86.42) and Port No (8069). 

Add servername in /etc/hosts file  
Example: 192.168.86.42  appserver.com appserver

```sh
192.168.86.42  appserver.com appserver
```

Step 7: Reload and Restart server
Reload server after change on default.conf in nginx
```sh
$ systemctl daemon-reload
$ systemctl restart nginx
$ systemctl restart restart
```

**Note:** Check firewall if connection is not available.

#### 2. Application Server:

**Step 1:** Update OS and Install nginx web server

_Update OS_  
```sh
$ sudo yum update -y
```
_Donwload python2 and install in Redhat 7_ 
```sh
$ yum install gcc openssl-devel bzip2-devel
$ cd /usr/src
$ wget https://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
$ tar xzf Python-2.7.16.tgz && cd Python-2.7.16
$ make altinstall
 
```
_Download PIP for Python_
```sh
$ curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
$ python2.7 get-pip.py
```


#### 3. Database Server:  

**Step 1:** Update OS and Install nginx web server


_Donwload Postgresql 10 for RedHat 7_ 
```sh
$ sudo rpm -Uvh https://yum.postgresql.org/10/redhat/rhel-6-x86_64/pgdg-redhat10-10-2.noarch.rpm
```

_Update OS_  
```sh
$ sudo yum update -y
```

_Install Postgresql 10 and install in RedHat 7_ 
```sh
$ sudo yum install postgresql10-server postgresql10 postgresql-contrib
$ sudo /usr/pgsql-10/bin/postgresql-10-setup initdb 
```

_Configure Postgresql 10 in RedHat 7 and Create user odoo_

```sh
$ sudo systemctl enable postgresql-10.service
$ sudo systemctl start postgresql-10.service
$ sudo su - postgres -c "createuser -s odoo" 2> /dev/null || true
```
## Source Repository

Source repository divided into 3 categeory depending on source used
#### Base Odoo Source
```
$ git clone -b 10.0 --single-branch https://github.com/odoo/odoo.git 10.0
```
#### Community Source
```
$ git clone -b oca --single-branch https://github.com/genweb2/gbs.git oca
$ git clone -b 10.0 --single-branch https://github.com/OCA/account-financial-tools.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/account-invoicing.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/operating-unit.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/partner-contact.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/web.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/reporting-engine.git
$ git clone -b 10.0 --single-branch https://github.com/OCA/server-tools.git

```
#### Application Source
```
$ git clone -b mtb_live --single-branch https://github.com/genweb2/gbs.git bank
$ git clone -b mtb_gbs_account --single-branch https://github.com/genweb2/gbs.git mtb_gbs_account
```

## Database Clean Query
```sql
-- Delete all Vendor Bills
delete from account_invoice_line;
delete from account_invoice;

-- Delete all Vendor Advance 
delete from vendor_security_deposit;
delete from vendor_security_return;
delete from vendor_bill_generation;
delete from vendor_bill_generation_line;
delete from vendor_advance;

-- Delete from Payment Instructions
delete from payment_instruction;

-- Delete from Bulk Import
delete from gbs_file_import_line;
delete from gbs_file_import;

-- Delete from TDS and VAT entries
delete from tds_vat_payment;
delete from tds_vat_challan;
delete from tds_vat_challan_line;

-- Delete all related entries
delete from account_asset_sale_line;
delete from account_asset_sale;
delete from account_asset_disposal_line;
delete from account_asset_disposal;
delete from account_asset_allocation_history;
delete from account_asset_depreciation_history_line;
delete from account_asset_depreciation_history;
delete from account_asset_depreciation_line;
delete from account_asset_asset;
delete from asset_depreciation_change_request;

-- Delete all Interface entries
delete from generate_cbs_journal_success;
delete from cbs_journal_line;
delete from server_file_error;
delete from server_file_error_line;
delete from server_file_success;
delete from gbs_data_migration;
delete from soap_process_error;
delete from system_date_status;

-- Delete all Journal Entries
delete from account_move_line;
delete from account_move;

-- Remove all Log related data
delete from auditlog_log_line;
delete from auditlog_log;
delete from auditlog_http_request;
delete from auditlog_http_session;
delete from ir_sessions;


-- Remove TPM related data
delete from tpm_branch_calculation_line;
delete from tpm_calculation_line;
delete from tpm_calculation;

-- Remove random data
delete from account_tax_slab_line;
delete from agreement;
delete from history_res_partner;
delete from res_partner where supplier=true;

-- Remove message data from related message table
delete from mail_message where model in ('tpm.branch.calculation.line');
delete from mail_message where model in ('tpm.calculation.line');
delete from mail_message where model in ('tpm.calculation');
delete from mail_message where model in ('account.move.line');
delete from mail_message where model in ('account.move');
delete from mail_message where model in ('server.file.error');
delete from mail_message where model in ('server.file.error.line');
delete from mail_message where model in ('server.file.success');
delete from mail_message where model in ('gbs.data.migration');
delete from mail_message where model in ('account.asset.sale.line');
delete from mail_message where model in ('account.asset.sale');
delete from mail_message where model in ('account.asset.disposal.line');
delete from mail_message where model in ('account.asset.disposal');
delete from mail_message where model in ('account.asset.allocation.history');
delete from mail_message where model in ('account.asset.depreciation.history.line');
delete from mail_message where model in ('account.asset.depreciation.history');
delete from mail_message where model in ('account.asset.depreciation.line');
delete from mail_message where model in ('account.asset.asset');
delete from mail_message where model in ('account.invoice.line');
delete from mail_message where model in ('account.invoice');
delete from mail_message where model in ('payment.instruction');
delete from mail_message where model in ('gbs.file.import.line');
delete from mail_message where model in ('gbs.file.import');
delete from mail_message where model in ('tds.vat.payment');
delete from mail_message where model in ('tds.vat.challan');
delete from mail_message where model in ('tds.vat.challan.line');
delete from mail_message where model in ('account.move.line');
delete from mail_message where model in ('account.move');
delete from mail_message where model in ('system.date.status');
```
