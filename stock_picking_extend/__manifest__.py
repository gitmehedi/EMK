# -*- coding: utf-8 -*-
{
    'name': "Stock Picking Extend",
    'summary': """
        This module is inherited module of Picking""",
    'description': """
        This module manage QC, Gate Pass and Transfer type(In or out delivery).
    """,
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Stock',
    'version': '10.0.0.1',
    'depends': [
        'stock_operating_unit_extend',
        'account',
        'gbs_product'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'report/inherit_stock_picking_report.xml',
        'wizard/inherit_stock_immediate_transfer_views.xml',
        'wizard/inherit_pack_operation_details_form.xml',
        'wizard/stock_date_of_transfer_wizard.xml',
        'views/stock_picking_views.xml',
    ],
}