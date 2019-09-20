{
    'name': 'Sales Delivery Schedules',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.0.1.0.0',
    'depends': [
        'product_sales_pricelist',
        'sales_team',
        'delivery_order',
        'stock',
        'ir_sequence_operating_unit',
        'report_layout',
    ],

    'data': [
        'data/delivery_schedule_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/delivery_schedules_view.xml',
        'reports/delivery_se_report.xml',
        'reports/delivery_se_report_templates.xml',
        'data/mail_template_data.xml',
        'views/inherited_stock_picking_views.xml',
        # 'views/delivery_schedules_date_wise_view.xml',
        # 'wizards/delivery_schedule_date_view.xml',

    ],

    'summary': 'Sales Delivery Schedules',
    'description':
    """Create Sales Delivery Schedules based on undelivered Delivery Orders""",
    'installable': True,
    'application': False,
}