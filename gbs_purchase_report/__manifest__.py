# -*- coding: utf-8 -*-
{
    'name': 'Purchase Report',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase Reports',
    'version': '10.0.0.1',
    'depends': [
        'purchase',
        'report_layout',
    ],
    'data': [
        'reports/purchase_requisition_report.xml',
        'wizard/purchase_requisition_wizard.xml',
    ],

    'summary': 'Purchase Requisition Report',
    'installable': True,
    'application': False,
}