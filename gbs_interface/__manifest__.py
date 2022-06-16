# -*- coding: utf-8 -*-

{
    "name": "GBS Interface",
    "summary": "GBS Interface",
    "version": "10.0.0.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'license': "AGPL-3",
    "category": "Tools",
    "depends": [
        'mail'
    ],
    "data": [
        "security/security.xml",
        # "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/menu_view.xml",
        "views/middleware_configuration_view.xml",
    ],
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": ["pysftp", "numpy"],
    },
}
