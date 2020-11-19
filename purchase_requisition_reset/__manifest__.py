{
    'name': 'Purchase Requisition Reset To Confirm',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase Requisition',
    'version':'10.0.1',
    'depends': [
        'purchase_requisition',
        'gbs_purchase_requisition'
    ],
    'data': [
        'views/purchase_requisition_view.xml'
    ],

    'description':
    "This module is for changing the Approved state to Confirm state of Purchase Requisition",
    'installable': True,
    'application': True,
}