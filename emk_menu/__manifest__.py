# -*- coding: utf-8 -*-

{
    'name': 'EMK Menu',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'EMK Menu',
    'version': '10.0.1.0.0',
    'category': 'Menu',
    'summary': '',
    'description': '',
    'depends': [
        'hr',
        'hr_payroll',
        'hr_holidays',
        'hr_recruitment',
        'hr_attendance',
        'stock',
        'calendar',
        'mail',
        'utm',
        'survey',
    ],
    'data': [
        'views/menu_view.xml',
    ],
    'installable': True,
    'application': True,
}
