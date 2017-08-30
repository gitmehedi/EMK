{
    'name': 'HR Payroll Arrear',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Payroll Arrear',
    'version': '1.0',
    'depends': ['hr'],
    'data': [
        #'security/ir.model.access.csv',
        'views/hr_payroll_arrear.xml',
        #'report/gbs_hr_meal_report.xml',
        #'report/gbs_hr_meal_report_templates.xml',
    ],

    'summary': 'Calculates HR Payroll Arrear Information',
    'description':
        """This module calculates the  arrear of the employee
            based on the condition'""",
    'installable': True,
    'application': True,
}