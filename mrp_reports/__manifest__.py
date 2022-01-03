# -*- coding: utf-8 -*-
{
    'name': "MRP Reports",

    'summary': """""",

    'description': """
    """,

    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',

    'category': 'Manufacturing',
    'version': '10.0.0.0.1',

    'depends': ['base', 'report_xlsx', 'report', 'mrp'],

    'data': [
        'wizards/production_report_wizard_view.xml',
        'reports/production_report_xlsx_view.xml'
    ],
}
