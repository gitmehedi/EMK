# -*- coding: utf-8 -*-
# Copyright 2016-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Account Department Dimension',
    'summary': 'Department information',
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'category': 'Accounting',
    'version': '10.0.1.0.0',
    'depends': [
        'account',
        'hr'
    ],
    'data': [
        'views/account_move.xml',
        'views/account_move_line.xml',
    ],
    'installable': True,
}
