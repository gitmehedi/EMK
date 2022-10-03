# -*- coding: utf-8 -*-
{
    'name': "GBS Invoice Line Qty Based On MRR or Delivery",

    'summary': """
    """,

    'description': """
    """,

    'author': "Genweb2 Limited",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','stock_picking_mrr','gbs_application_group'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/inherited_vendor_bill.xml',
        'views/inherited_customer_invoice.xml',
    ],

}