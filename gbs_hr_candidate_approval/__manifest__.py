{
    'name': 'GBS HR Candidate Approval',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'employee',
    'version': '1.0',
    'depends': [
        'hr',
        'hr_recruitment',
        'gbs_application_group',
        'hr_employee_operating_unit',
    ],

    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/gbs_hr_candidate_approval_view.xml',
    ],

    'summary': 'GBS HR Candidate Selection Approval Process',
    'installable': True,
    'application': True,
}