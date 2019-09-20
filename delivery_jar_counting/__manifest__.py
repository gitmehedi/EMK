{
    'name': 'Delivery JAR Count',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.1.1.1',
    'depends': [
        'gbs_application_group',
        'account',
        'sale',
        'delivery_order', # for jar count
        'product_sales_pricelist', # for packing
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/uom_jar_summary_view.xml',
        'wizards/partner_selection_wizard_view.xml',
        'views/jar_received_view.xml',
        'reports/partner_wise_jar_summary_report_view.xml',
        'reports/jar_summary_analytic_report_view.xml',
    ],

    'summary': 'Delivery JAR Count',
    'installable': True,
    'application': False,
}