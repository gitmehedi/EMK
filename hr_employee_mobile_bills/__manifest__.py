{
    'name': 'Employee Mobile Bills',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Employee Mobile Bills',
    'version':'1.0',
    'depends': ['hr','report_layout','gbs_hr_security'],
    'data': [
        'security/ir.model.access.csv',
        #'security/ir_rule.xml',
        'views/hr_mobile_bill_view.xml',
        'views/hr_emp_mb_bill_view.xml',
        'views/hr_emp_mb_bill_limit_view.xml',
        'report/gbs_hr_mobile_report.xml',
        'report/gbs_hr_mobile_report_templates.xml',
    ],
    
    'summary': 'Calculates Employees Mobile Bills',
    'description': 
    """This module calculates the moblile bills of the employee
        based on the condition'""",        
    'installable': True,
    'application': True,
}