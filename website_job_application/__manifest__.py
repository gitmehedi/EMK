{
    'name': 'Job Application',
    'category': 'Web',
    'summary': 'Extend Job Application Module',
    'author': 'Md. Mehedi Hasan',
    'website': 'https://github.com/gitmehedi',
    'depends': ['web','hr_recruitment','website_hr_recruitment'],
    'data': [
        'views/inherited_hr_applicant_views.xml',
        'views/inherited_website_hr_recuitment_templates.xml',
        'report/applicant_form_report.xml',
        'report/applicant_form_report_template.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/template.xml'
    # ],
    # 'js': [
    #     'static/src/js/chrome.js'
    # ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
