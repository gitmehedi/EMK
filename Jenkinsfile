pipeline{
    agent any
    stages{
        stage("Init"){
            steps{
                sh "sudo systemctl stop mtb.service"
            }
        }
        stage("Build"){
            steps{
                sh "sudo -u odoo -i git --git-dir=/odoo/custom/10.0/mtb/mtb_qa/.git --work-tree=/odoo/custom/10.0/mtb/mtb_qa/ pull"
                sh "sudo -u odoo -i git --git-dir=/odoo/custom/10.0/mtb/mtb_gbs_account/.git --work-tree=/odoo/custom/10.0/mtb/mtb_gbs_account/ pull"
            }
        }
        stage("Run"){
            steps{
                sh "sudo -u odoo /odoo/virtualenv/mtb/bin/python /odoo/server/10.0/odoo-bin -c /etc/gbs/mtb.conf -d ${MTBL_DB} -u ${MTBL_APPS} &"
                sh "sleep 10m"
            }
        }
        stage("Kill"){
            steps{
                sh "sudo kill -9 \$(pgrep -f mtb.conf) 1> /dev/null 2> /dev/null"
            }
        }
        stage("Final Run"){
            steps{
                sh "sudo systemctl start mtb.service"
            }
        }
        
    }
}
