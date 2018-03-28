# -*- coding: utf-8 -*-

{
    'name': 'Purchase Work Order',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Purchase',
    'summary': """ Puchase Work Order """,
    'description': """
        Work Order
        Place work order which is store all work order information about
        product quantity, product price, production terms, delivery date with many optional condition.
    """,
    'depends': [
        'purchase',
        'custom_report',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/purchase_production_terms_views.xml',
        'views/work_order_views.xml',
        'report/work_order_report_view.xml',
    ],
    'installable': True,
    'application': True

}
