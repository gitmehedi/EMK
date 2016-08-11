# -*- coding: utf-8 -*-

{
    'name': 'HR Organization Calendar',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Calendar',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/clone_calendar_wizard_views.xml',
        'views/organization_calendar_menu.xml',
        'views/calendar_holidays_view.xml',
        'views/calendar_holiday_type_view.xml',


    ],
    'depends': ['calendar','account_period'],
    'summary': 'Customizable calendar for organizations',
    'description':
        """Organization calendar
        1. Admin can modify the setting
        2. Calendar can be cloned
        3. Weekly & Public holiday can be set

        """,
    'installable': True,
    'application': True,
}