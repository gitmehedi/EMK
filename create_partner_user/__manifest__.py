# -*- coding: utf-8 -*-
{
    'name': "Partner to User",
    'version': '1.0',
    'summary': """
        Create a Login/User from a partner""",
    'description': """
        Long description of module's purpose
    """,
    'license': 'AGPL-3',
    'author': "git.mehedi@gmailc.com",
    'website': "",
    'category': 'base',
    'version': '0.1',
    'depends': ['base', 'membership_user'],
    'data': [
        'wizard/user_view.xml',
        'views/partner_views.xml',
        'views/templates.xml',
    ],
}
