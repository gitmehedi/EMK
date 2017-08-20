{
    'name': 'GBS Sales Customer Credit Limited',
    'version': '1.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sale',
    'depends': [
        'gbs_application_group',
        'sale',
    ],
    'data': [
        'report/credit_limit_report.xml',
        'report/credit_limit_report_template.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizards/customer_creditlimit.xml',
        'views/limit_view.xml',
        'views/partner_inherit_view.xml',

    ],
    'summary': 'This module handles request of customer credit limit',
    'description':"GBS Sales Customer Credit Limited",
    'installable': True,
    'application': True,
}
