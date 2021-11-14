# -*- coding: utf-8 -*-
{
    'name': "GBS Employee Cost Center Link",

    'summary': """
        Link employee with cost center""",

    'description': """
        Link employee with cost center
    """,

    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": '10.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'operating_unit', 'hr', 'account_cost_center', 'gbs_hr_attendance'],

    # always loaded
    'data': [
        # 'views/inherited_operating_unit_view.xml',
        'views/inherited_hr_employee_view.xml',
    ],

}
