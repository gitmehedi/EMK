{
    'name': 'Custom Report for Accounting',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'accounting',
    'depends': ['base_setup', 'product', 'analytic', 'report', 'web_planner'],
    'data': [
        'report/account_invoice_report_view.xml',
    ],

    'description': 'Custom Report for Accounting',
    'installable': True,
    'application': False,
}