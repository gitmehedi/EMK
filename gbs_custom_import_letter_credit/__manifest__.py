{
    'name': 'GBS Custom Import Letter Credit',
    'summary': '',
    "category": "Accounting",
    'description': 'Analytic account creation on creating lc import(local/foreign)',
    'author': 'Genweb2',
    'license': 'AGPL-3',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'letter_of_credit'
    ],
    'data': [
        'views/inherited_lc_credit_local_form.xml',
        'views/inherited_lc_import_foreign_view.xml',
        'wizards/update_import_lc_number_confirmation.xml'
    ],

}
