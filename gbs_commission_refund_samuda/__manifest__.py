# -*- coding: utf-8 -*-
{
    'name': 'Samuda Commission Refund Claim',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version': '10.0.1.0.0',
    'sequence': 14,
    'depends': [
        'base',
        'account',
        'gbs_commission_refund',
        'gbs_commission_config'
    ],
    'data': [
        # data
        'data/sequence.xml',
        'data/service_data.xml',
        'security/ir.model.access.csv',

        # views
        # 'views/purchase_order_view.xml',
        'views/account_invoice_view.xml',
        'views/inherited_purchase_order_view.xml',

    ],
    'summary': '',
    'description': """
==============================

Key Features
------------
* Commission and Refund Claiming Process""",
    'installable': True,
    'application': False,
}
