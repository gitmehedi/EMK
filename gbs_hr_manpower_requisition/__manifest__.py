{
    'name': 'GBS HR Manpower Requisition',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'employee',
    'version': '1.0',
    'depends': [
        'hr',
        'hr_recruitment',
        'gbs_application_group',
    ],

    'data': [
        'security/security.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/gbs_hr_manpower_requisition_view.xml',
        'views/hr_department_inherit_view.xml',
    ],

    'summary': 'GBS HR Manpower Requisition',
    'installable': True,
    'application': True,
}
