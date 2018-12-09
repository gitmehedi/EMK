{
    'name': 'GBS Purchase MRR',
    'summary': """
        Update MRR quantity in PR line.
        """,
    'description': """
        This module relate between PR to MRR.
        Show MRR list in PO.
        Update PR lines MRR quantity.
    """,
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase',
    'version':'10.0.1',

    'depends': [
        'gbs_purchase_order',
        'stock_picking_mrr',
    ],
    'data': [
        'views/stock_view.xml',
        'views/po_view.xml',
    ],
    'installable': True,
    'application': False,
}