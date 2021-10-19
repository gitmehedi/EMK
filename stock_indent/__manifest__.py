{
    'name': 'Indent Management',
    'version': '10.0.1',
    'category': 'Warehouse Management',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'license': 'AGPL-3',
    'complexity': "normal",
    'depends': ['account',
                'gbs_stock_product',
                'ir_sequence_operating_unit',
                'indent_type',
                'stock_operating_unit_user',
                'inventory_user',


                ],
    'data': [
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'report/stock_indent.xml',
        'data/stock_indent_data.xml',
        'data/stock_indent_sequence.xml',
        'data/stock_indent_scrap_sequence.xml',
        'views/stock_location_view.xml',
        'views/stock_indent_view.xml',
        'views/stock_picking_type.xml',
        'views/receive_products.xml',
        'views/stock_scrap_view.xml'
    ],
    'installable': True,
    'application': False,
}
