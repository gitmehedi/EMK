# -*- coding: utf-8 -*-
{
    'name': "GBS Samuda Service Order",
    'summary': """Samuda Service Order""",
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Purchase Order',
    'version': '10.0.0.1',
    'depends': [
        'purchase', 'ir_sequence_operating_unit', 'gbs_purchase_order', 'purchase_operating_unit'
    ],
    'sequence': 10,
    'data': [
        'security/security.xml',
        'data/service_data.xml',
        'views/service_order_views.xml',
        'views/inherited_purchase_view.xml',
        'report/service_order_report.xml'
    ]
}
