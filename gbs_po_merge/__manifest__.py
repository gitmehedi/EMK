# -*- coding: utf-8 -*-
{
    'name': "GBS Quotation Merge",

    'summary': """
        To merge the quotation and create new quotation.""",

    'description': """
        This module give the option to merge multiple quotation. 
        Also in one quotation can add to another qoutation 
    """,

    'author': "Genweb2 Limited",
    'website': "https://www.genweb2.com",

    'category': 'Purchase',
    'version': '10.0.1',
    'depends': [
        'gbs_purchase_order',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'wizard/po_merge_wizard_view.xml',
        'views/gbs_purchase_order_views.xml',
    ],
}