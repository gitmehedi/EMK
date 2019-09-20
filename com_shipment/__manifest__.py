{
    'name': 'Shipment',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1',
    'depends': [
        'mail',
        'commercial',
        'letter_of_credit',
        'gbs_supplier',
    ],

    'data': [
            'views/shipment_view.xml',
            'views/shipment_menu.xml',
            'wizard/on_board_wizard_view.xml',
            'wizard/done_wizard_view.xml',
            'wizard/cancel_wizard.xml',
            'wizard/eta_wizard_view.xml',
            'wizard/send_to_cnf_wizard_view.xml',
            'wizard/doc_receive_wizard_view.xml',
            'wizard/cnf_clear_wizard_view.xml',
            'wizard/cnf_approve_quotation_wizard_view.xml',
            'wizard/email_template_view.xml',
    ],

    'summary': 'LC Shipment',
    'installable': True,
    'application': False,
}