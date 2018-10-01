{
    'name': 'Stock Summary Reports',
    'version': '10.0.0.1',
    'author': 'Genweb2',
    'website': 'www.genweb2.com',
    'category': 'Warehouse Management',
    'depends': [
        'report_layout',
        'stock_operating_unit',
        'gbs_stock_product',
        'gbs_product_cost_price_history',
    ],
    'summary': "This module generate custom report for stock summary",
    'description': """
        Customize reporting module to generate report by product category,
        unit wise and in between date range.
    """,
    'data': [
        'data/default_data.xml',
        'wizard/print_report_view.xml',
        'report/stock_inventory_report_view.xml',

    ],
    'installable': True,
    'application': True,
}
##############################################################################

