# -*- coding: utf-8 -*-
{
    'name': "Stock Issue Report",

    'summary': """
        Custom Report Of Issue Product""",

    'description': """
        By this report user can get the record of 
        issued product list by departmental and periodical.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': ['stock_indent','report_layout'],

    'data': [
        'security/ir.model.access.csv',
        'report/stock_issue_report.xml',
        'wizard/stock_issue_wizard.xml',

    ],

}