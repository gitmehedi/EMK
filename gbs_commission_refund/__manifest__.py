# -*- coding: utf-8 -*-
{
    'name': 'GBS Commission Refund',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version': '10.0.1.0.0',
    'sequence': 14,
    'depends': [
        'base',
        'product_sales_pricelist',
        'sale',
        'gbs_sale_order_approval',
        'account',
        'hr',
        'customer_business_type',
        'gbs_commission_config',
        'gbs_samuda_sales_return'
    ],
    'data': [
        # data
        'data/account_journal_data.xml',

        # security
        'security/ir.model.access.csv',

        # views
        'views/account_invoice_view.xml',
        'views/commission_refund_acc_config_view.xml',
        'views/product_sales_pricelist_view.xml',
        'views/res_partner_view.xml',

        # wizards
        'wizards/inherited_stock_return_picking.xml',

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
