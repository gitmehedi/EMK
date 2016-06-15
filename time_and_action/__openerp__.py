# -*- coding: utf-8 -*-
##############################################################################
# Time and Action Module
##############################################################################
{   
    'name': 'Time and Action',
    'summary': """Lakshma Time and Action Module""",
    'version': '0.1',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Garments & Apparels',
    'description': '''Time and Action Module:
     (Description will provide later).''',
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'views/root_menu.xml',
             'views/related_process_views.xml',
             'views/task_creation_views.xml',

             ],
    'depends': ['account','stock'],
    'installable': True,
    'application': True,
}
