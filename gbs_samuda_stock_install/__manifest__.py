# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Stock Install",

    'summary': """
        Installetion Module for Inventory""",

    'description': """
        All inventory related modules are install by this module. 
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': [
        'stock_indent',
        'gbs_stock_product',
        'ir_sequence_operating_unit',
        'indent_type',
        'gbs_stock_scrap',
        'item_loan_process',
        'stock_move_backdating',
        'stock_operating_unit_extend',
        'stock_operating_unit_user',
        'stock_picking_extend',
        'stock_picking_lc',
        'stock_picking_mrr',
        'stock_warehouse_extend',
        'stock_gate_in',
        'stock_custom_summary_report',
        'stock_purchase_custom_report',
        'stock_loan_analysis_report',
        'stock_transfer_report',
        'stock_issue_report',
        'stock_inventory_extend',
        'stock_picking_loan',

    ],

    'installable': True,
    'application' : True,
}