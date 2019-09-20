# -*- coding: utf-8 -*-

{
    'name': 'EMK HR Employee',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'EMK HR Employee',
    'version': '10.0.1.0.0',
    'data': [
        'views/inherit_hr_employee.xml',
        'views/inherit_hr_contract.xml',
    ],
    'depends': [
        'hr',
        'hr_contract',
        'hr_short_leave',
        'l10n_in_hr_payroll',
        'survey',
    ],
    'category': 'HR',
    'summary': '',
    'description': '',
    'installable': True,
    'application': True,
}
