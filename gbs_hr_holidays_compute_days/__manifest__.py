# -*- coding: utf-8 -*-
{
    'name': 'GBS Employee Compute Leave Days',
    'version': '10.0.1.0.0',
    'sequence': 30,
    'category': 'Human Resources',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': """Computes the actual leave days 
               considering rest days and public holidays""",
    'depends': ['hr',
                'hr_contract',
                'hr_holidays',
                'gbs_hr_public_holidays'
                ],
    'data': [
        'views/hr_holidays_status.xml',
        'views/hr_holidays_view.xml',
#         'security/ir.model.access.csv',

    ],
    'installable': True,
    'application': True,
}
