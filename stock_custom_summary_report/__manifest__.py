{
    'name': 'Stock Summary Reports',
    'version': '10.0.0.1',
    'author': 'Genweb2',
    'website': 'www.genweb2.com',
    'category': 'Warehouse Management',
    'depends': [
        'base',
        'report',
        'custom_report',
        'stock_operating_unit',
    ],
    'summary': "This module generate custom report for stock summary",
    'description': """
        Customize reporting module to generate report by product category,
        unit wise and in between date range.
    """,
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'data/default_data.xml',
        'wizard/print_report_view.xml',
        # 'views/inherite_layout.xml',
        # 'views/inherited_product_template_views.xml',
        # 'views/inherited_product_category_view.xml',
        'report/stock_inventory_report_view.xml',

    ],
    'installable': True,
    'application': True,
}
##############################################################################

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
