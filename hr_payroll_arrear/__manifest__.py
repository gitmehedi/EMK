{
    'name': 'Payroll Arrear',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Payroll Arrear',
    'version': '10.0.1.0.0',
    'depends': ['hr',
        'hr_payroll',
        'l10n_in_hr_payroll',
        'gbs_hr_security'
        ],
    'data': [
        'security/ir.model.access.csv',
        #'security/ir_rule.xml',
        'views/hr_payroll_arrear.xml',
    ],

    'summary': 'Calculates HR Payroll Arrear Information',
    'description':
        """This module calculates the  arrear of the employee
            based on the condition'""",
    'installable': True,
    'application': True,
}