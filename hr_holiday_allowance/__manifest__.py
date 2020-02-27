{
    'name': 'HR Holiday Allowance',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Human Resources',
    'version': '1.0',
    'data': [
        'security/ir.model.access.csv',
        'wizard/holiday_allowance_wizard_view.xml',
        'views/holiday_allowance_view.xml'
    ],
    'depends': [
        'hr',
        'resource',
        'operating_unit',
        'hr_employee_operating_unit',
        'gbs_hr_package'
    ],

    'description':
        "This module enables employee Holiday Allowance",
    'installable': True,
    'application': True,
}