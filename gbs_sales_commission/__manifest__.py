{
    'name': 'GBS Sales Commission',
    'version': '10.0.1.0.0',
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
        'security/ir.model.access.csv',
        'views/inherited_res_partner_views.xml',
        'views/customer_commission_configuration_views.xml',
        'views/inherited_products_template_view.xml',
        'report/commission_report.xml',
        ],
    'description': 'GBS Sales Commission',
    'installable': True,
    'application': False,
}
