{
    'name': 'Delivery Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version': '10.1.1.1',
    'depends': [
        'delivery_order',
        'report_xlsx',
        'report',
        'stock'
    ],
    'data': [
        'reports/delivery_report_xlsx_view.xml',
        'reports/undelivered_report_xlsx_view.xml',
        'wizards/delivery_report_wizard_view.xml',
        'wizards/undelivered_report_wizard_view.xml'
    ],
    'summary': 'Different type of delivery reports of products',
    'installable': True,
    'application': False,
}
