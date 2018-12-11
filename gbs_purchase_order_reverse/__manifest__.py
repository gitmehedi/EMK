{
    'name': 'GBS Purchase Order Reverse',
    'summary': """
        Approved PO can be reset.
        """,
    'description': """
        This module set option to take approved PO in Quotation stage.
    """,
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase',
    'version':'10.0.1',

    'depends': [
        'gbs_purchase_rfq',
    ],
    'data': [
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': False,
}