{
    'name': 'HR Payslip Extend',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Payslip Extend',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'hr_payslip_menu.xml'
    ],
    'depends': [
        'hr_payroll',
        ],
    'summary': 'Calculates Employees Earned Leave',
    'description': 
    """This module calculates the earned leave of the employee 
        based on the condition of yearly/monthly/Quarterly'""",        
    'installable': True,
    'application': True,
}