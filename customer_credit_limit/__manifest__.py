{
    'name': 'Customer Credit Limit',
    'version': '10.0.1.0.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'sales',
    'depends': [
        'gbs_application_group',
        'sale',
        'base',
        'sales_team',
        'account',
        'stock',
        'report_layout',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/credit_limit_report.xml',
        'report/credit_limit_report_template.xml',
        #'security/ir_rule.xml',
        'wizards/customer_creditlimit.xml',
        'views/limit_view.xml',
        'views/partner_inherit_view.xml',

    ],
    'summary': 'This module handles request of customer credit limit',
    'description':"Customer Credit Limit",
    'application': False,
}
