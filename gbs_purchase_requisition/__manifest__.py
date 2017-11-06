{
    'name': 'GBS Purchase Requisition',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase Requisition',
    'version':'10.0.1',
    'depends': [
        'purchase_requisition',
        'stock_indent',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/gbs_purchase_requisition_view.xml',
    ],

    'description': 
    "This module are compatible for PR",
    'installable': True,
    'application': True,
}