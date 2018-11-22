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
        # 'security/security.xml',
        # 'security/ir_rule.xml',
        # 'security/ir.model.access.csv',
        'wizard/rfq_wizard.xml',
        'wizard/rfq_email_template.xml',
        'report/rfq_report.xml',
        'report/rfq_send_report.xml',
        'report/comparative_bid_study_report.xml',
        'data/rfq_sequence.xml',
        'data/mail_template_data.xml',
        'views/pr_view.xml',
        'views/po_view.xml',
        'views/purchase_rfq_view.xml',
    ],

    'description': 
    "This module are compatible for PR",
    'installable': True,
    'application': True,
}