{
    'name': 'HR Employee Meal Bills',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Employee Meal Bills',
    'version':'1.0',
    'depends': ['hr',
                'report_layout',
                'gbs_hr_security',
                'operating_unit',
                'gbs_read_excel_utility'
                ],
    'data': [
        'security/ir.model.access.csv',
        #'security/ir_rule.xml',
        'views/hr_meal_bill_view.xml',
        'report/gbs_hr_meal_report.xml',
        'report/gbs_hr_meal_report_templates.xml',
        'wizards/hr_employee_meal_bills_import_wizard_views.xml',
        'wizards/success_wizard.xml'
    ],
    
    'summary': 'Calculates Employees Meal Information',
    'description': 
    """This module calculates the  bills of the employee
        based on the condition'""",        
    'installable': True,
    'application': True,
}