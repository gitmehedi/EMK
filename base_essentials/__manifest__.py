# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Base Essentials',
    'version': '1.3',
    'category': 'Hidden',
    'description': """
The essentials addon of Odoo, needed for all installation.
===================================================
""",
    'depends': ['base',
    'auditlog',
    'auto_backup',
    'password_security',
    'auth_admin_passkey',
    'limit_login_attempts',
    'web_responsive',
    'web_access_rule_buttons'],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
}
