# -*- coding: utf-8 -*-
{
    'name': "Cron Job Notification",
    'version': '1.0',
    'summary': """
        Send Notification through email to the following users when a cron job succeed or fail""",
    'description': """
        Cron Job Notification
    """,
    'license': 'AGPL-3',
    'author': "Genweb2 Limited",
    'website': "",
    'category': 'base',
    'version': '0.1',
    'depends': ['base', 'mail'],
    'data': [
        'views/inherited_ir_cron_view.xml',
        'data/email_template.xml'
    ],
}