{
    'name': 'Payroll Arrear OT',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Payroll Arrear OT',
    'version': '10.0.1.0.0',
    'depends': ['hr',
        'hr_payroll',
        'hr_payroll_arrear',
        'hr_payroll_ot'
        ],
    'data': [
        'data/data.xml',
        'views/hr_payroll_arrear_ot.xml',

    ],

    'summary': 'Calculates HR Payroll Arrear OT Information',
    'description':
        """This module calculates the  arrear ot of the employee
            based on the condition'""",
    'installable': True,
    'application': False,
}