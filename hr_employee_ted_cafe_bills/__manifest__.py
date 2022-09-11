{
    'name': 'Employee Ted Cafe Bills',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Employee Ted Cafe',
    'summary': 'Calculates Employees Mobile Bills',
    'description': """This module calculates the ted cafe bills 
                    of the employee
                    based on the condition'""",
    'version': '1.0',
    'depends': ['hr',
                'hr_payroll',
                'l10n_in_hr_payroll',
                'report_layout',
                'point_of_sale',
                'pos_users',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'wizards/contract_employee_wizard_view.xml',
        'wizards/employee_credit_sale_wizard_view.xml',
        'views/hr_ted_cafe_bill_view.xml',
        'views/hr_ted_cafe_credit_sale_view.xml',
        'views/point_of_sale_view.xml',
    ],

    'installable': True,
    'application': True,
}
