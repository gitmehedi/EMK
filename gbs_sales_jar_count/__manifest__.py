{
    'name': 'Sales JAR Count',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.1.1.1',
    'depends': [
        'gbs_application_group',
        'account',
        'sale',
        'delivery_order', # for jar count
        'product_sales_pricelist',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/uom_jar_summary_view.xml',
        'views/jar_received_view.xml',
        'wizards/partner_selection_wizard_view.xml',
        'reports/partner_wise_jar_summary_report_view.xml',
        'reports/jar_summary_analytic_report_view.xml',
    ],

    'summary': 'Summary of Jar taken or returned',
    'installable': True,
    'application': False,
}