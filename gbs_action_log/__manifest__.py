# -*- coding: utf-8 -*-
{
    'name': 'GBS Users Action Log',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Log',
    'version': '10.0.0.1',
    'depends': [
        'gbs_purchase_requisition',
        'gbs_purchase_order',
        'stock_picking_mrr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/users_action_data.xml'
    ],

    'summary': 'Users Action Log',
    'installable': True,
    'application': False,
}
