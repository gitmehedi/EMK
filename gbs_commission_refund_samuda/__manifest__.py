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

        # views
        # 'views/purchase_order_view.xml',
        'views/account_invoice_view.xml',
        'views/inherited_purchase_order_view.xml',
        'views/sale_order_view.xml',

    ],
    'summary': 'Override base module logic.',
    'description': """
GBS Product Unit Price Update module
==============================

Key Features
------------
* Product Unit Price Update for Local Purchase at "Anticipatory Stock".
* Product Unit Price will not Update for Foreign Purchase.
* Finish Goods Unit Price Update at Production""",
    'installable': True,
    'application': False,
}
