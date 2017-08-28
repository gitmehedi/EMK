# -*- coding: utf-8 -*-
{
    'name': "Base Package",

    'summary': """
        This module will install base required addons.""",

    'description': """
        This module will install base required addons.
    """,

    'author': "Genweb2 Limited",
    'website': "http://www.genweb2.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                # 'web_export_view',
                # 'web_chatter_paste',
                'disable_odoo_online',
                'base_technical_features',
                'web_hide_db_poweredby_link',
                'hide_desktop_notification_link'],

    # always loaded
    'data': [
        'security/security.xml',
    ],
}