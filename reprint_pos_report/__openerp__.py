{
    'name': "Reprint PoS Sale Ticket",
    'author': 'Genweb2 Limited',
    'website': "http://www.genweb2.com",
    'category': 'Point of Sale',
    'version': '0.1',
    'summary': """
        Reprint point of sale report from backend 
    """,
    'description': """
        Reprint point of sale report from backend
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
        'report/reprint_sale_ticket_view.xml',
        'wizard/pos_product_return_view.xml',
        'views/inherit_pos_order_view.xml',

    ],
    'installable': True,
    'application': True,
}
