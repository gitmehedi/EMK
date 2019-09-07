{
    'name': 'GBS File Import',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Tools',
    'version':'10.0.0.1',
    'summary': "Custom module to import file in system",
    'description': "Import excel file and save data \
                      Process data for glip",
    'data': [
        'security/ir.model.access.csv',
        'wizards/gbs_file_import_wizard_view.xml',
        'views/gbs_file_import_view.xml',
        # 'views/gbs_imported_data_view.xml',

    ],

    'depends': [
        'account','mtbl_access',
    ],

    'installable': True,
    'application': True,
}