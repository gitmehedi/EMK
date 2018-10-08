{
    'name': 'Data Import',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Data Import',
    'version':'10.0.1.0.0',
    'summary': """Manage all kind of csv file upload and import data""",
    'description': """To data import easily and manage data properly by csv file format this module will help.""",
    'data': [
        'wizards/data_import_wizard_view.xml',
    ],
    
    'depends': [
        'event',
    ],
  
    'installable': True,
    'application': True,
}