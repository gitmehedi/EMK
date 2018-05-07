# -*- coding: utf-8 -*-
{
    'name': "Stock Issue Report",

    'summary': """
        Summary of Stock Issue Report
        """,

    'description': """
        
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Warehouse Management',
    'version': '10.0.1.0.0',

    'depends': ['stock_indent','custom_report'],

    'data': [
        # 'security/ir.model.access.csv',
        'report/stock_issue_report.xml',
        'wizard/stock_issue_wizard.xml',

    ],

}