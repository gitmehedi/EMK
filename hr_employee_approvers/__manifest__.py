# -*- coding: utf-8 -*-
{
    'name': "HR Employee Approvers",

    'summary': """
        To manage the custom approver chain""",

    'description': """
        By this module You can customize the approver chain for employee and also can manage the access rule.
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'HR',
    'version': '10.0.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_holidays_multi_levels_approval'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # 'views/views.xml',
    ],
}