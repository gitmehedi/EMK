{
    'name': 'Delivery Authorization',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.1.1.1',
    'depends': [
        'sale',
        'gbs_application_group',
        'sale_stock',
        'product_sales_pricelist',
        'account',
        'sale_order_type',
        'gbs_pi_creation',
        'letter_of_credit',
        'gbs_sales_commission_so',
        'amount_to_word_bd',
        'report_layout',
        'delivery_challan_report',
        'ir_sequence_operating_unit',
        'gbs_samuda_stock',
    ],

    'data': [
        'security/security.xml',
        'report/delivery_order_report.xml',
        'report/delivery_order_report_template.xml',
        'wizards/letter_of_credits_view.xml',
        'wizards/do_max_order_qty_without_lc_views.xml',
        'views/delivery_order_view.xml',
        'views/delivery_authorization_view.xml',
        'views/inherited_account_payment_view.xml',
        'report/money_receipt_paperformat.xml',
        'report/cash_received_report.xml',
        'report/cash_received_report_view.xml',
        'views/inherit_stock_picking_view.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/delivery_authorization_sequence.xml',
        'data/delivery_order_sequence.xml',
        'views/stock_indent_inherit.xml',
    ],

    'summary': 'Delivery Authorization',
    'description':
    """Create Delivery Authorization based on specific Sales Order""",
    'installable': True,
    'application': False,
}