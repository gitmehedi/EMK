{
    'name': 'HR Employee Other Allowance',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Other Allowance',
    'version': '10.0.1.0.0',
    'depends': ['hr','gbs_hr_security'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_other_allowance.xml',
    ],

    'summary': 'Calculates HR Other Allowance Information',
    'description':
        """This module calculates the  other allowance of the employee
            based on the condition'""",
    'installable': True,
    'application': True,
}