{
    'name': 'Sales Delivery Authorization',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Delivery Order',
    'version':'1.0',
    'depends': [
        'sale',
        'product_sales_pricelist'
    ],
    'data': [
        'report/delivery_order_report.xml',
        'report/delivery_order_report_template.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/delivery_order_view.xml',
    ],
    'summary': 'Sales delivery Order/Authorization Information',
    'description': 
    """This module is discribing all delivery authorization information""",
    'installable': True,
    'application': True,
}