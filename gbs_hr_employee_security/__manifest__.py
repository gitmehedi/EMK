# -*- coding: utf-8 -*-
{
    'name': "GBS HR Employee Security",

    'summary': """
        Manage customize security of Employee Records""",

    'description': """  """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'HR',
    'version': '10.0.1',

    'depends': ['hr'],

    'data': [
        'wizard/emp_sub_action_wizard_view.xml',
        'security/ir_rule.xml',
        'views/hr_employee_views.xml',
    ],

}