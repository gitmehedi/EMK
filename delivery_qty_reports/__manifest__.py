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
        'custom_report',
        'stock_operating_unit',
    ],

    'data': [
        'security/ir.model.access.csv',
        'reports/process_delivery_report_view.xml',
        'reports/process_monthly_delivery_report_view.xml',
        'wizards/daily_delivery_report_wizard_view.xml',
        'wizards/monthly_delivery_report_wizard_view.xml',
    ],

    'summary': 'Different delivered & undelivered reports of products',
    'installable': True,
    'application': False,
}