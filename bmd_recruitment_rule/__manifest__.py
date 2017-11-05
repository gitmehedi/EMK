{
    'name': 'BMD Recruitment Rule',
    'summary': 'Extend Job Application Module',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'depends': ['website_job_application','gbs_bd_district'],
    'data': [
        'security/ir.model.access.csv',
        'views/bmd_inherit_hr_applicant.xml',
        'views/bmd_inherit_job_position_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
