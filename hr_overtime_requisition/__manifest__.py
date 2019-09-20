{
    'name': 'HR OverTime Requisition',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'HR Attendance',
    'version':'1.0',
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/hr_overtime_requisition_view.xml'
    ],
    'depends': [
        'hr',
        'hr_attendance',
        'resource',
        'operating_unit',
        'hr_holidays_multi_levels_approval',
        'gbs_application_group',
        ],
    'summary': 'This Module is use for OverTime Requisition.',
    'installable': True,
    'application': True,
}