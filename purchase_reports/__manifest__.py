{
    'name': 'Purchase Reports',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Purchase Reports',
    'version':'1.0',
    'depends': ['letter_of_credit',
                'report_layout',
                ],
    'data': [
        'report/pending_purchase_templates.xml',
        'report/pending_purchase_report_wizard.xml',
        'view/menu_items.xml',
    ],
    
    'summary': 'Purchase Reports Information',
    'installable': True,
    'application': True,
}