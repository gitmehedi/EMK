{
    'name': 'Shipment',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'1.0.0',
    'depends': [
        'commercial',
        'letter_of_credit',
    ],

    'data': [
            'views/shipment_view.xml',
            'views/shipment_menu.xml',
            'wizard/on_board_wizard_view.xml',
            'wizard/gate_in_wizard_view.xml',
            'wizard/eta_wizard_view.xml',
            'wizard/doc_receive_wizard_view.xml',
            'wizard/cnf_quotation_wizard_view.xml',
            'wizard/cnf_clear_wizard_view.xml',
            'wizard/cnf_approve_quotation_wizard_view.xml',
    ],

    'summary': 'LC Shipment',
    'installable': True,
    'application': False,
}