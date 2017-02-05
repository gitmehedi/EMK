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
    "depends": ["hr_payroll"],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "security/menu.xml",
    ],
    'installable': True,
    'application': True,
}
