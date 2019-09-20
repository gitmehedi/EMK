{
    'name': 'HR Employee Other Deduction',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Other Deduction',
    'version': '10.0.1.0.0',
    'depends': ['hr',
                'hr_payroll',
                'l10n_in_hr_payroll',
                'gbs_hr_security'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_other_deduction.xml',
    ],

    'summary': 'Calculates HR Other Deduction Information',
    'description':
        """This module calculates the  other deduction of the employee
            based on the condition'""",
    'installable': True,
    'application': True,
}