# -*- coding: utf-8 -*-
{
    'name': "Samuda Dashboard",
    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    'summary': """
        This module will install base required addons.""",
    'description': """
        This module will install base required addons.
    """,
    "depends": ["crm"],
    'data': [
        "views/menu.xml",
        "views/dashboard.xml"
    ],
    'installable': True,
    'application': True,
}
