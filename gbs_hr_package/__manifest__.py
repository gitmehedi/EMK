# -*- coding: utf-8 -*-
{
    'name': "HR Package",

    'summary': """
        This module will install required addons in HR domain.""",

    'description': """
        This module will install required addons in HR domain.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
                'hr',
                'hr_holidays',
                'hr_recruitment',
                # 'gbs_hr_calendar',
                #'hr_experience',
                'gbs_hr_department_sequence',
                'gbs_application_group',
                'gbs_hr_employee_documents',
                # 'gbs_hr_employee_seniority'
    ],

    # always loaded
    'data': ['security/ir.model.access.csv',
             'security/hr_security.xml',

    ],
}