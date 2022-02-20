{
    'name': 'GBS Gender',
    'summary': 'General Gender Types',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'depends': [
        'mail_send',
        'base',
        'point_of_sale',
    ],
    'data': [

        'views/inherit_account_journal.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
