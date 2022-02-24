{
    'name': 'Job Application',
    'category': 'Website',
    'summary': 'Extend Job Application Module',
    'author': 'Genweb2 Limited',
    'website': 'https://genweb2.coom',
    'depends': ['web',
                'hr_recruitment',
                'website_hr_recruitment',
                'gbs_bd_district'
                ],
    'data': [
        'report/report_paperformat1.xml',
        'report/applicant_form_report.xml',
        'report/applicant_form_report_template.xml',
        # 'views/website_hr_recruitment_templates.xml',
        'views/inherited_website_hr_recruitment_templates.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/template.xml'
    # ],
    # 'js': [
    #     'static/src/js/chrome.js'
    # ],
    'installable': True,
    'application': True,
}
