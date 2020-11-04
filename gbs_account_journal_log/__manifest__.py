{
    'name': 'Account Journal Log',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'accounts',
    'version': '10.1.1.1',
    'sequence': 31,
    'depends': [
        'account',
    ],
    'data': [
        'views/account_journal_view.xml',
        'views/inherit_account_move_view.xml',
        'views/inherit_account_move_line_view.xml',
        'views/inherit_account_move_view_style.xml',
    ],

    'summary': 'Account Journal Log',
    'description':
    """Creating log for journal item""",
    'installable': True,
    'application': False,
}