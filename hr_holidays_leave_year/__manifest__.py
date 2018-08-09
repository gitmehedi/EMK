{
    'name': 'HR Holidays Leave Year',
    'version': '1.0.0',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'category': 'Human Resources',
    'summary': """Computes the actual leave days 
               considering rest days and public holidays""",
    'depends': ['hr',  
                'hr_holidays',
                ],
    'data': [
#         'views/hr_holidays_status.xml',
        'views/hr_holidays_view.xml',
#         'security/ir.model.access.csv',
#         'security/ir_rule.xml',
    ],
    'installable': True,
    'application': True,
}
