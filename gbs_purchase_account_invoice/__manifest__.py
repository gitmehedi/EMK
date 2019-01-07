{
    'name': 'GBS Purchase Account Invoice',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase Management',
    'version':'10.0.0.1',
    'summary': """
        Inherited Purchase Account Invoice Module""",

    'description': """
        To manage the purchase account invoice.
        Control Supplier Bill.
    """,
    'depends': [
        'gbs_purchase_order',
        'stock_picking_lc',
    ],
    'data': [
        # 'views/account_invoice.xml',
    ],

    'installable': True,
    'application': False,
}