{
    'name': 'Sales Delivery Schedule Entry',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version':'10.1.1.1',
    'depends': [
        'sale',
        'product_sales_pricelist',
        'account',
        'sale_order_type',
    ],

    'data': [
        # 'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        # 'report/delivery_order_report.xml',
        # 'report/delivery_order_report_template.xml',
          'views/delivery_schedule_entry_view.xml',
        # 'views/inherited_account_payment_view.xml',
    ],

    'summary': 'Sales Delivery Schedule Entry',
    'description':
    """Create Sales Delivery Schedule Entry based on specific Sales Order""",
    'installable': True,
    'application': True,
}