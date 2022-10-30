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
    'category': 'Purchase Order',
    'version': '10.0.1',

    'depends': ['purchase', 'purchase_requisition', 'gbs_purchase_rfq', 'gbs_application_group'],
    'data': [
        'views/lib.xml',
        'views/purchase_rfq_cs_views.xml',
        'views/purchase_rfq_views_separated.xml',
        'views/purchase_cs_menu.xml',
        'views/inherited_purchase_rfq_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
