{
    'name': 'Letter of Credit Done(LC)',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Commercial',
    'version':'10.0.1.0.0',
    'depends': [
        'com_shipment',
        'question_set',
    ],

    'data': [
            'wizards/lc_evaluation_wizard_view.xml',
            'wizards/confirmation_wizard_view.xml',
            'views/lc_done.xml',
    ],
    'images': [
        # 'static/description/icon.png',
    ],

    'summary': 'Letter of Credit (LC) Done',
    'installable': True,
    'application': False,
}