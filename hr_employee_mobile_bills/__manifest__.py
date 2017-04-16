{
    'name': 'HR Employee Mobile Bills',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Employee Mobile Bills',
    'version':'1.0',
    'depends': ['hr'],
    'data': [
        'views/hr_employee_loan_line_view.xml',
    ],
    
    'summary': 'Calculates Employees Mobile Bills',
    'description': 
    """This module calculates the moblile bills of the employee
        based on the condition'""",        
    'installable': True,
    'application': True,
}