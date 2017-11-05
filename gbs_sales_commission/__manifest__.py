{
    'name': 'GBS Sales Commission',
    'version': '1.0',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Sales',
    'depends': [
        'gbs_application_group',
        'sale',
        'sales_team',
        'report'
    ],
    'data': [
        'views/inherited_res_partner_views.xml',
        'views/customer_commission_configuration_views.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'report/commission_report.xml'
        ],
    'description': 'GBS Sales Commission',
    'installable': True,
    'application': True,
}
