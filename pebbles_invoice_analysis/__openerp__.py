# -*- coding: utf-8 -*-
##############################################################################
{
    'name' : 'PEBBLES INVOICE ANALYSIS',
    'version' : '1.0',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category' : 'Accounting & Finance',
    'depends': ['account'],
    'data': [
        # 'security/account_security.xml',
        # 'security/ir.model.access.csv',
        'wizard/pebbles_account_invoice_wizard_view.xml',
        'report/pebbles_account_invoice_report_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
