# -*- coding: utf-8 -*-
{
    'name': "Loan Integration With Payroll",
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'summary': """
        This module integrate employees monthly mobile bill with payroll.""",
    'description': """
        This module integrate employees monthly mobile bill with payroll.
    """,
    "depends": [
        'hr',
        'hr_payroll',
        'l10n_in_hr_payroll',
        'hr_employee_loan'
    ],
    'data': [
        'data/hr_payroll_data.xml',
        #'views/inherited_hr_payslip_views.xml'
    ],
    'application': False,
}
