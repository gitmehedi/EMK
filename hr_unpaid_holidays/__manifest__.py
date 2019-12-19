# -*- coding: utf-8 -*-
{
    'name': 'Unpaid Holidays',
    'version': '10.0.1.0.0',
    'sequence': 30,
    'category': 'Human Resources',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': """Computes the actual leave days 
               considering rest days and public holidays""",
    'depends': ['hr_holidays'],
    'data': [
        'views/hr_holidays_status.xml',
    ],
    'installable': True,
    'application': False,
}
