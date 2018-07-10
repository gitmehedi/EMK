{
    'name': 'Membership Registration',
    'version': '1.0',
    'category': 'Sales',
    'author': 'erp@genweb2.com',
    'website': 'https://genweb2.com/',
    'summary': 'Registration form for Membership. Applicant provide necessary information to become member.',
    'description': """
This module allows you to register members for memberships.
=========================================================================

It supports different kind of members:
--------------------------------------
    * Free member
    * Associated member (e.g.: a group subscribes to a membership for all subsidiaries)
    * Paid members
    * Special member prices

It is integrated with sales and accounting to allow you to automatically
invoice and send propositions for membership renewal.
    """,
    'depends': ['membership', 'gbs_bd_district'],
    'data': [
        # 'report/report_paperformat1.xml',
        # 'report/applicant_form_report.xml',
        # 'report/applicant_form_report_template.xml',
        # 'views/inherited_hr_applicant_views.xml',
        'views/membership_registration_templates.xml',
    ],
    'installable': True,
    'application': True,
}
