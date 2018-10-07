# -*- coding: utf-8 -*-
{
    'name': "GBS Stock Scrap",

    'summary': """
        Approval Process and Report for Scrapped Material
        """,

    'description': """
        Approval Process for Scrapped Material.
        Report For Scrapped Material And Their Source Document.
        """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.0.1',

    'depends': ['stock_operating_unit'],

    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/stock_scrap_views.xml',
    ],
}