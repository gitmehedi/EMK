{
    'name': 'GBS HR Recruitment',
    'author': 'Genweb2',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Recruitment Process',
    'description': """
Manage the recruitment process
================================================

This application allows you to easily keep track of jobs, manpower requisition, candidate selection approval process.
""",
    'depends': [
        'hr',
        'base',
        'hr_recruitment',
        'gbs_hr_recruitment_access_rights',
        'gbs_hr_job_extend',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/gbs_hr_candidate_approval_view.xml',
        'views/gbs_hr_manpower_requisition_view.xml',
        'views/hr_department_inherit_view.xml',
        'views/hr_applicant_inherit_view.xml',
        'report/appointment_letter_template.xml',
        # 'report/demo_appointment_letter.xml',
        'data/sequence.xml',
        # 'data/letter_template_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}