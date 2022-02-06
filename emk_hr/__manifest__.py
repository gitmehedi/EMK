# -*- coding: utf-8 -*-

{
    'name': 'EMK HR Employee',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'EMK HR Employee',
    'version': '10.0.1.0.0',
    'category': 'HR',
    'summary': '',
    'description': '',
    'depends': [
        'hr',
        'hr_contract',
        'l10n_in_hr_payroll',
        'hr_attendance',
        'operating_unit',
        'date_range',
        'survey',
        'hr_recruitment_survey',
        'hr_experience',
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'views/inherit_hr_employee_view.xml',
        'views/inherit_hr_contract_view.xml',
        'views/inherit_hr_experience_view.xml',
        'views/inherit_hr_contract_type_view.xml',
    ],
    'installable': True,
    'application': True,
}
