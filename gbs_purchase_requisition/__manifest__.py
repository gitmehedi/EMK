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
        'commercial',
        'gbs_application_group',
    ],
    'data': [
        'data/pr_sequence.xml',
        'security/security.xml',
<<<<<<< HEAD
        # 'security/ir_rule.xml',
=======
        'security/ir_rule.xml',
>>>>>>> 0fc72e3522217e2d75adcce24e8795bfe11c1605
        'security/ir.model.access.csv',
        'wizard/pr_wizard_view.xml',
        'wizard/pr_from_where_wizard_view.xml',
        'views/gbs_purchase_requisition_view.xml',
        'views/pr_commercial_menu_views.xml',
        'views/stock_indent_view.xml',
    ],

    'description': 
    "This module are compatible for PR",
    'installable': True,
    'application': True,
}