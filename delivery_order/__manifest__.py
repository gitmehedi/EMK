{
    'name': 'Delivery Authorization',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.1.1.1',
    'depends': [
        'sale',
        'sale_stock',
        'product_sales_pricelist',
        'account',
        'sale_order_type',
        'letter_of_credit',
        'gbs_pi_creation',
        'letter_of_credit',
        'gbs_sales_commission_so',
        'stock',
        'amount_to_word_bd',
        'custom_report',
    ],

    'data': [
        'security/ir.model.access.csv',
        'report/delivery_order_report.xml',
        'report/delivery_order_report_template.xml',
        'wizards/letter_of_credits_view.xml',
        'wizards/do_max_order_qty_without_lc_views.xml',
        'views/delivery_order_view.xml',
        'views/delivery_order_layer_view.xml',
        'views/inherited_account_payment_view.xml',
        'report/money_receipt_paperformat.xml',
        'report/cash_received_report.xml',
        'report/cash_received_report_view.xml',

    ],

    'summary': 'Delivery Authorization',
    'description':
    """Create Delivery Authorization based on specific Sales Order""",
    'installable': True,
    'application': False,
}