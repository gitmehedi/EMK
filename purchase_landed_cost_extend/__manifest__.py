# -*- coding: utf-8 -*-

{
    'name': 'Purchase landed costs extend',
    'version': '10.0.2.0.0',
    'author': 'Genweb2',
    'category': 'Purchase Management',
    'website': 'www.genweb2.com',
    'summary': 'Purchase cost distribution',
    'description': 'Purchase cost distribution',
    'depends': [
        'purchase_landed_cost',
        'stock_picking_extend',
        'account',
        'gbs_application_group',
        'base',
        'gbs_samuda_analytic_vendor_bills',
        'product_gate_in'
    ],
    'data': [
        'security/security.xml',
        'data/landed_cost_sequence.xml',
        'views/purchase_cost_distribution_view.xml',
        'views/purchase_expense_type_view.xml',
        'views/stock_picking_view.xml',
        'views/landed_cost_view.xml',
        'views/inherited_purchase_cost_distribution_line.xml',
        'wizard/analytic_account_wizard.xml',
        'wizard/inherit_picking_import_wizard.xml',
        'wizard/picking_import_wizard_view.xml',
        'wizard/journal_entry_post_wizard.xml',
        'security/ir.model.access.csv',
        'views/remove_existing_landed_cost_options.xml'
    ],
    'installable': True,
    'application': False
}
