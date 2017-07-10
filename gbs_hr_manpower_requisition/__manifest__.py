{
    'name': 'GBS HR Manpower Requisition',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'employee',
    'version': '1.0',
    'depends': [
        'hr',
        'hr_recruitment',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/gbs_hr_manpower_requisition_view.xml',
    ],

    'summary': 'GBS HR Manpower Requisition',
    'installable': True,
    'application': True,
}
