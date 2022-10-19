{
    'name': 'GBS Purchase CS Process',
    'summary': """
        Purchase CS Process.
        """,
    'description': """
        This module relate between PR to CS.
    """,
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase',
    'version': '10.0.1',

    'depends': ['purchase', 'purchase_requisition', 'gbs_purchase_rfq'],
    'data': [
        'views/lib.xml',
        'views/inherited_purchase_rfq_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
