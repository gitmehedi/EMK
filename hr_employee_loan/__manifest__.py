{
    'name': 'HR Employee Loan',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Employee Loan',
    'version':'1.0',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/ir_rule.xml',
        'views/menuitems.xml',
        'views/hr_employee_loan_policy_view.xml',
        'views/hr_employee_loan_proof_view.xml',
        'views/hr_employee_loan_view.xml',
        'views/hr_employee_loan_type_view.xml',
        'wizards/hr_reschedule_loan.xml',

    ],
    
    'summary': 'Calculates Employees Loan',
    'description': 
    """This module calculates the loan of the employee 
        based on the condition'""",        
    'installable': True,
    'application': True,
}