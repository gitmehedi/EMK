{
    'name': 'HR Public Holidays',
    'version': '10.0.1.0.0',
    'sequence': 30,
    'category': 'Human Resources',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "Manage All kinds of Public Holiday",
    'depends': [
        'hr',
        'hr_holidays',
        'hr_payroll',
        'operating_unit',
        'hr_holiday_year',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/hr_calendar_clone_wizard_view.xml',
        'views/hr_public_holidays_view.xml',
        'views/hr_holidays_calendar_view.xml',
    ],
    'installable': True,
    'application': True,
}
