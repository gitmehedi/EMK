# -*- coding: utf-8 -*-
{
    'name': "Stock Issue Due Report",

    'summary': """
        Custom Report Of Issue Due Product""",

    'description': """
        By this report user can get the record of 
        issued product and due list by departmental and periodical.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Stock',
    'version': '10.0.1',

    'depends': ['stock_indent','report_layout'],

    'data': [
        'report/stock_issue_due_report.xml',
        'wizard/stock_issue_due_wizard.xml',

    ],

}