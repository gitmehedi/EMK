{
    'name': 'Purchase Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase Reports',
    'version':'1.0',
    'depends': ['letter_of_credit',
                'report_layout',
                'date_range'
                ],
    'data': [
        'view/inherit_date_range_view.xml',
        'report/pending_purchase_templates.xml',
        'report/purchase_matrial_req_template.xml',
        'report/purchase_summary_template.xml',
        'report/pr_summary_template.xml',
        'wizards/pending_purchase_report_wizard.xml',
        'wizards/purchase_matrial_req_wizard.xml',
        'wizards/purchase_summary_wizards.xml',
        'wizards/pr_summary_wizard.xml',
        'wizards/pr_summary_wizard_2.xml',
        'view/menu_items.xml',
    ],
    
    'summary': 'Purchase Reports Information',
    'installable': True,
    'application': True,
}