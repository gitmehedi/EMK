# -*- coding: utf-8 -*-

{
    'name': 'HR Absence Summary',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Calendar',
    'data': [
        # 'report/absence_report_view.xml',
        # 'report/absence_report_pdf.xml',
        'views/menu_view.xml',
        'report/employee_absence_view.xml',
    ],
    'depends': ['calendar', 'mail'],
    'summary': 'Customizable calendar for organizations',
    'description':
        """Organization Summary
        1. Admin can create report end of the month
        """,
    'installable': True,
    'application': True,
}
