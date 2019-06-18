# Genweb2 Business Solution [GBS]
## Mutual Trust Bank Limited [MTBL]
In 3-tier architecture, there is an intermediary level, meaning that the architecture is generally split up between: 
1. **The Client or Web server**, i.e. the computer, which requests the resources, equipped with a user interface 
(usually a web browser) for presentation purposes; 
2. **The Application Server** (also called middleware), whose task it is to provide the requested resources, but by calling on another server.
3. **The Data Server**, which provides the application server with the data that it requires: 

**MTBL** follows 3-tier architecture

### 3-tier Installtions:

1. **Client/Web Server**:

**Step 1:** Update OS and Install nginx web server

_Update OS_  
```
$ sudo yum update -y
```
_Donwload nginx and install in Redhat 7_ 
```
$ wget http://nginx.org/packages/rhel/7/x86_64/RPMS/nginx-1.14.2-1.el7_4.ngx.x86_64.rpm
$ sudo yum install yum install nginx-1.14.2-1.el7_4.ngx.x86_64.rpm -y 
```

**Step 2:** Configure nginx with OS  

_Create symbolic link for nginx_
```
$ sudo systemctl enable nginx
```
**_Start of nginx_** 
```
$ sudo systemctl start nginx
```
**_Stop of nginx_** 
```
$ sudo systemctl stop nginx
```
**_Retart of nginx_** 
```
$ sudo systemctl restart nginx
```
**_Status of nginx_** 
```
$ sudo systemctl status nginx
```
**Step 3:** Additional configuration of nginx  

**_Open 80 and 442 port using firewall-cmd_**  
Install ```firewalld``` OS package with configuration in redhat.  
```
$ sudo yum install firewalld -y
$ sudo systemctl enable firewalld
$ sudo systemctl start firewalld
```
You must open and enable port 80 and 443 using the firewall-cmd command:
```
$ sudo firewall-cmd --permanent --zone=public --add-service=http
$ sudo firewall-cmd --permanent --zone=public --add-service=https
$ sudo firewall-cmd --reload
```
**Step 5:** Testing nginx configuration
```
$ sudo ss -tulpn
```

**Step 6:** Configure nginx server

Create a default configuration file in nginx folder /etc/nginx/conf.d/default.conf
Content of file.
```
upstream odoo {
 server 192.168.86.42:8010;
}
upstream odoochat {
 server 192.168.86.42:8072;
}

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
           # proxy_redirect off;
             proxy_pass "http://192.168.86.42:8010";
             proxy_set_header Host $host;
        }
         location /longpolling {
            proxy_pass "http://192.168.86.42:8072";
        }

}
```
**_Note_**: Change IP(192.168.86.42) and Port No (8069). 

Add servername in /etc/hosts file  
Example: 192.168.86.42  appserver.com appserver

```
192.168.86.42  appserver.com appserver
```

Step 7: Reload and Restart server
Reload server after change on default.conf in nginx
```
$ systemctl daemon-reload
$ systemctl restart nginx
$ systemctl restart restart
```

**Note:** Check firewall if connection is not available.

2. **Application Server**:

**Step 1:** Update OS and Install nginx web server

_Update OS_  
```
$ sudo yum update -y
```
_Donwload python2 and install in Redhat 7_ 
```
$ yum install gcc openssl-devel bzip2-devel
$ cd /usr/src
$ wget https://www.python.org/ftp/python/2.7.16/Python-2.7.16.tgz
$ tar xzf Python-2.7.16.tgz && cd Python-2.7.16
$ make altinstall
 
```
_Download PIP for Python_
```
$ curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
$ python2.7 get-pip.py
```


3. **Data Server**:  

**Step 1:** Update OS and Install nginx web server


_Donwload Postgresql 10 for RedHat 7_ 
```
$ sudo rpm -Uvh https://yum.postgresql.org/10/redhat/rhel-6-x86_64/pgdg-redhat10-10-2.noarch.rpm
```

_Update OS_  
```
$ sudo yum update -y
```

_Install Postgresql 10 and install in RedHat 7_ 
```
$ sudo yum install postgresql10-server postgresql10
$ sudo /usr/pgsql-10/bin/postgresql-10-setup initdb 
```

_Configure Postgresql 10 in RedHat 7 and Create user odoo_

```
$ sudo systemctl enable postgresql-10.service
$ sudo systemctl start postgresql-10.service
$ sudo su - postgres -c "createuser -s odoo" 2> /dev/null || true
```