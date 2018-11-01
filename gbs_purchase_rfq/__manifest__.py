{
    'name': 'GBS Purchase RFQ',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase',
    'version':'10.0.1',
    'depends': [
        'gbs_purchase_order',
    ],
    'data': [
        # 'data/pr_sequence.xml',
        # 'security/security.xml',
        # 'security/ir_rule.xml',
        # 'security/ir.model.access.csv',
        'wizard/rfq_wizard.xml',
        'views/pr_view.xml',
        # 'report/gbs_rfq_report.xml',
    ],

    'description': 
    "This module are compatible for PR",
    'installable': True,
    'application': True,
}