# -*- coding: utf-8 -*-

{
    'name': 'EMK HR Employee',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'EMK HR Employee',
    'version': '10.0.1.0.0',
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/inherit_hr_employee.xml',
        'views/inherit_hr_contract.xml',
    ],
    'depends': [
        'hr',
        'hr_contract',
        'l10n_in_hr_payroll',
        'hr_attendance',
        'operating_unit',
        'date_range',
        'survey',
    ],
    'category': 'HR',
    'summary': '',
    'description': '',
    'installable': True,
    'application': True,
}
