{
    'name': 'Samuda Account Reports',
    'version': '10.0.0.1',
    'author': 'Genweb2',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'depends': [
        'account_reports',
        'report_xlsx',
        'report',
    ],
    'summary': "This module generate custom account reports",
    'description': """
        Customize reporting module to generate report by product wise,
        unit wise and in between date range.
    """,
    'data': [
        'reports/profit_loss_with_realization_xlsx_view.xml',
        'wizard/profit_loss_with_realization_view.xml',
    ],
    'installable': True,
    'application': False,
}
