{
    "name": "POS Reports",
    "version": "8.0.0.1.0",
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    "category": "Point Of Sale",
    'summary': 'POS Summary Reports',
    'description': """
    """,
    "depends": ['base', 'point_of_sale', 'operating_unit','stock'],
    'data': [
        'wizard/pos_summary_report_wizard_view.xml',
        'wizard/warehouse_to_shop_distribution_report_wizard_view.xml',
        'report/pos_order_report_view.xml',
        'report/warehouse_to_shop_distribution_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
