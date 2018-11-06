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
        'data/mail_template_data.xml',
        'views/pr_view.xml',
    ],

    'description': 
    "This module are compatible for PR",
    'installable': True,
    'application': True,
}