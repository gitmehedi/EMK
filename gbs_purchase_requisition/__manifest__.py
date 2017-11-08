{
    'name': 'GBS Purchase Requisition',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase Requisition',
    'version':'10.0.1',
    'depends': [
        'purchase_requisition',
        'stock_indent',
        'ir_sequence_operating_unit',
    ],
    'data': [
        'data/pr_sequence.xml',
        'security/security.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizard/pr_wizard_view.xml',
        'views/gbs_purchase_requisition_view.xml',
    ],

    'description': 
    "This module are compatible for PR",
    'installable': True,
    'application': True,
}