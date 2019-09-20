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
        'report',
        'account',
        'report_layout',
        #'gbs_sales_commission_so',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/inherited_res_partner_views.xml',
        'views/customer_commission_configuration_views.xml',
        'views/inherited_products_template_view.xml',
        'views/sales_commission_generate_views.xml',
        'report/commission_report.xml',
        'report/customer_commission_summary.xml',
        'views/inherited_account_invoice_view.xml',
        'report/commission_due_report_view.xml',
    ],

    'description': 'GBS Sales Commission',
    'installable': True,
    'application': False,
}