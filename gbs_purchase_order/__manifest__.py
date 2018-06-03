# -*- coding: utf-8 -*-
{
    'name': "GBS Purchase Order",

    'summary': """
        Custom Purchase Order""",

    'description': """
        To manage the purchase order,quotation and revision . 
    """,

    'author': "Genweb2 Limited",
    'website': "https://www.genweb2.com",

    'category': 'Uncategorized',
    'version': '10.0.1',
    'depends': [
        'purchase_order_revision',
        'gbs_purchase_requisition',
        'commercial',
        'ir_sequence_operating_unit',
        'stock_operating_unit_extend',
        'custom_report',
        'amount_to_word_bd',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/sequence_po.xml',
        'report/purchase_order_report.xml',
        'wizard/po_wizard_view.xml',
        'views/gbs_purchase_order_views.xml',
    ],
}