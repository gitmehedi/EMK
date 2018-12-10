{
    'name': 'Employee IOU',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'employee',
    'version': '10.0.1.0.0',
    'depends': [
        'hr',
        'gbs_hr_security'
    ],

    'data': [
        'security/ir.model.access.csv',
        #'security/ir_rule.xml',
        'wizard/hr_employee_iou_wizard_views.xml',
        'views/hr_employee_iou_view.xml',
    ],

    'summary': 'HR Employee IOU',
    'application': False,
}
