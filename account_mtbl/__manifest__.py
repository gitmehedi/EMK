# -*- coding: utf-8 -*-

{
    "name": "MTBL GL Master Data",
    "summary": "Master Data of mtbl",
    "version": "10.0.1.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    "category": "Generic",
    "depends": [
        "base",
        'operating_unit',
        'account',
        'sub_operating_unit',
        'account_operating_unit',
        'mail',
    ],
    "data": [
        'views/segment_view.xml',
        'views/servicing_channel.xml',
        'views/acquiring_channel.xml',
        'views/inherit_res_currency.xml',
        'views/inherit_account_journal.xml',
        'views/inherit_res_bank.xml',
        'views/inherit_account_move.xml',
        'views/inherit_account_type.xml',
        'views/mtbl_branch.xml',
    ],
    'installable': True,
    'application': True,
}
