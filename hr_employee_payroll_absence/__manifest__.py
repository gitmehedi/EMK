{
    'name': 'Employee Payroll Absence',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Employee Payroll Absence',
    'summary': 'Calculates Employees Employee Payroll Absence',
    'description': """This module calculates the Absence 
                    of the employee based on the condition'""",
    'version': '1.0',
    'depends': ['hr',
                'hr_payroll',
                'l10n_in_hr_payroll',
                'report_layout',
                'point_of_sale',
                'hr_attendance'
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/contract_employee_wizard_view.xml',
        'views/hr_employee_payroll_absence_view.xml',
    ],
    'installable': True,
    'application': True,
}
