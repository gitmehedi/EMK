{
    'name': 'Daily Delivery Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'sales',
    'version':'1.1.1',
    'depends': [
        'stock',
        'sale',
        'sales_team',
    ],

    'data': [
        'wizards/daily_delivery_report_wizard_view.xml',
        'reports/inherit_stock_picking_report.xml',
        'reports/inherit_stock_picking_report_view.xml',
    ],

    'summary': 'Different delivered & undelivered reports of products',
    'installable': True,
    'application': False,
}