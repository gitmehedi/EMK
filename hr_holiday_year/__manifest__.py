{
    'name': 'HR Holiday Year',
    'version': '10.0.2',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    'summary': """Computes the actual leave days 
               considering rest days and public holidays""",
    'depends': ['hr_holidays',
                'date_range',
                ],
    'data': [
#         'views/hr_holidays_status.xml',
        'views/hr_holidays_view.xml',
        'views/date_range_view.xml',
#         'security/ir.model.access.csv',
#         'security/ir_rule.xml',
    ],
    'installable': True,
    'application': True,
}
