# -*- coding: utf-8 -*-

{
    'name': 'HR Organization Summary',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Calendar',
    'data': [
        # 'report/absence_report_views.xml',
    ],
    'depends': ['account_period','calendar','hr_organization_calendar'],
    'summary': 'Customizable calendar for organizations',
    'description':
        """Organization Summary
        1. Admin can create report end of the month
        """,
    'installable': True,
    'application': True,
}