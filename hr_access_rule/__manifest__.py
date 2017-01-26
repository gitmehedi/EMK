# -*- coding: utf-8 -*-
{
    'name': "HR Access Rule",

    'summary': """
        This module will install base required addons.""",

    'description': """
        This module will install base required addons.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",
    "depends": ["hr"],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/menu.xml",
        # "security/hr_employee.xml",
#         "security/ir.model.access.csv",
    ],
    'installable': True,
    'application': True,
}
