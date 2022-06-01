# -*- coding: utf-8 -*-

{
    'name': 'Security Installation',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Module Installation',
    'summary': 'Install all Security related module',
    'description': 'Install all Security related module',
    'version': '1.0',
    'depends': [
        'tko_web_sessions_management',
        'inherit_tko_web_sessions_management',
        'url_access_restriction',
        'app_odoo_customize',
        'limit_login_attempts',
        'auditlog',
        'hidden_admin',
        'mass_editing',
        'password_security',
        'auth_admin_passkey',
        'web_access_rule_buttons',
        'web_export_view',
    ],
    'installable': True,
    'application': True,
}
