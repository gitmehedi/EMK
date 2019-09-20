{
    'name': 'Daily & Monthly Delivery Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'sales',
    'version':'1.1.1',
    'depends': [
        'stock',
        'sale',
        'sales_team',
        'report_layout',
        'stock_operating_unit',
        'delivery_order',
    ],

    'data': [
        'reports/process_delivery_report_view.xml',
        'reports/process_deli_undeli_report_view.xml',
        'reports/process_monthly_delivery_report_view.xml',
        'wizards/daily_delivery_report_wizard_view.xml',
        'wizards/daily_deli_undeli_report_wizard_view.xml',
        'wizards/monthly_delivery_report_wizard_view.xml',
        'views/menu.xml',
    ],

    'summary': 'Different delivered & undelivered reports of products',
    'installable': True,
    'application': False,
}