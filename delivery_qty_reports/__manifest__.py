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
        'reports/process_delivery_report_view.xml',
        'wizards/daily_delivery_report_wizard_view.xml',
    ],

    'summary': 'Different delivered & undelivered reports of products',
    'installable': True,
    'application': False,
}