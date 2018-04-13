{
    'name': 'Product Gate In',
    'version': '10.1.0.1',
    'category': 'Commercial',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles purchase product gate in process in a customized business logic way.",
    'depends': [
        'com_shipment','hr_employee_operating_unit','stock','gbs_procure_to_pay_access','letter_of_credit','shipment_lc_product','commercial',
    ],

    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/product_get_in_view.xml',
        'views/inherited_purchase_shipment_view.xml',
        'data/gate_in_sequence.xml'
    ],
    'installable': True,
    'application': True,
}