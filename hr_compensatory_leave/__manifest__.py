{
    'name': 'HR Compensatory Leave',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'summary': 'This modules calculates compensatory leave depending on OT Requests',
    'version': '1.0',
    'depends': [
        'hr_overtime_requisition',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/menu_view.xml',
        'views/hr_compensatory_leave_view.xml',
        'views/hr_compensatory_leave_allowance_view.xml',
    ],
    'installable': True,
    'application': True,
}
