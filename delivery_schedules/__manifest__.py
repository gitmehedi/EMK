{
    'name': 'Sales Delivery Schedules',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.0.1.0.0',
    'depends': [
        'product_sales_pricelist',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/delivery_schedules_view.xml',
        'reports/delivery_se_report.xml',
        'reports/delivery_se_report_templates.xml',
        'data/mail_template_data.xml',
    ],

    'summary': 'Sales Delivery Schedules',
    'description':
    """Create Sales Delivery Schedules based on specific Sales Order""",
    'installable': True,
    'application': False,
}