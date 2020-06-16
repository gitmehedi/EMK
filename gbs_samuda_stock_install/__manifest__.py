# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Stock Installer",

    'summary': """
        Installation Module for Inventory""",

    'description': """
        All inventory related modules are install by this module. 
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': [
        'stock_assign_picking',
        'stock_indent',
        'indent_operating_unit',
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
        'stock_custom_summary_report',
        'stock_purchase_custom_report',
        'stock_loan_analysis_report',
        'stock_transfer_report',
        'stock_issue_due_report',
        'stock_issue_report',
        'stock_inventory_extend',
        'stock_picking_loan',
        'gbs_product_cost_price_history',
        'gbs_samuda_inventory_access',
    ],

    'installable': True,
    'application' : True,
}