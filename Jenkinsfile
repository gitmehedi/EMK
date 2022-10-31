pipeline{
    agent any
    stages{
        stage("Init"){
            steps{
                sh "sudo systemctl stop emk.service"
            }
        }
        stage("Build"){
            steps{
                sh "sudo -u odoo -i git --git-dir=/odoo/custom/10.0/emk/.git --work-tree=/odoo/custom/10.0/emk pull"
            }
        }
        stage("Run"){
            steps{
                sh "sudo -u odoo /odoo/virtualenv/emk/bin/python /odoo/server/10.0/odoo-bin -c /etc/gbs/emk.conf -d ${EMK_DB} -u ${EMK_APPS} &"
                sh "sleep 15m"
            }
        }
        stage("Kill"){
            steps{
                sh "sudo kill -9 \$(pgrep -f emk.conf)"
            }
        }
        stage("Final Run"){
            steps{
                sh "sudo systemctl start emk.service"
            }
        }
    }
}
