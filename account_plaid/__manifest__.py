# -*- coding: utf-8 -*-
{
    'name': "account_plaid",

    'summary': """
        Use Plaid.com to retrieve bank statements""",

    'description': """
        Use Plaid.com to retrieve bank statements.
    """,

    'category': 'Accounting',
    'version': '2.0',

    'depends': ['account_online_sync'],

    'data': [
        'views/plaid_views.xml',
    ],
    'qweb': [
        'views/plaid_templates.xml',
    ],
    'license': 'OEEL-1',
}
