{
    'name': 'HR Employee Meal Bills',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Employee Meal Bills',
    'version':'1.0',
    'depends': ['hr',
                'report_layout',
                'gbs_hr_security'],
    'data': [
        'security/ir.model.access.csv',
        #'security/ir_rule.xml',
        'views/hr_meal_bill_view.xml',
        'report/gbs_hr_meal_report.xml',
        'report/gbs_hr_meal_report_templates.xml',
    ],
    
    'summary': 'Calculates Employees Meal Information',
    'description': 
    """This module calculates the  bills of the employee
        based on the condition'""",        
    'installable': True,
    'application': True,
}