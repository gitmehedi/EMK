{
    'name': 'LC Sales Common Function',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1.0.0',
    'depends': [
        'gbs_sale_order_approval',
        'letter_of_credit',
        'com_shipment',
        'shipment_lc_product',
        'gbs_pi_creation',
        'gbs_document_type',
        'report_layout',
        'amount_to_word_bd',
        'product_harmonized_system',
        'account',
        'gbs_sale_order_approval',
        'gbs_application_group',
    ],

    'data': [
        'views/sales_tree_view.xml',
        'views/commercial_sales.xml',
        'views/lc_sales_menu.xml',
        'wizard/reset_lc_line_wizard_view.xml',
    ],

    'summary': 'Sale By LC',
    'installable': True,
    'application': False,
    'auto_install': True
}