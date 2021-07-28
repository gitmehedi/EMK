# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": 'Document PDF Thumbnail',
    "version": '1.0',
    "description": """
        Document PDF Thumbnail
    """,
    "author": 'Odoo Experts',
    "website": 'https://www.odooexperts.nl',
    "category": "Discuss",
    'images': [],
    "depends": [
        'base',
        'mail',
        #'mrp',
    ],
    "init_xml": [],
    'data': ['views/ir_attachment_view.xml'],
    "qweb": ['static/src/xml/thread.xml'],
    "test": [],
    "demo_xml": [],
    "installable": True,
    'auto_install': False,
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
