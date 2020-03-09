# -*- coding: utf-8 -*-
{
    'name': 'Fixed Assets Management (FAM)',
    'description': """ Main module for asset management which include all css,js and image files.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'base',
        'operating_unit',
        'sub_operating_unit',
        'account_asset',
        'account',
    ],
    'data': [
        'security/security.xml',
        # 'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu_view.xml',
        'views/server_action_views.xml',
        'wizard/asset_modify_views.xml',
        'wizard/asset_allocation_wizard_view.xml',
        'wizard/account_asset_type_wizard_view.xml',
        'wizard/asset_dispose_wizard_view.xml',
        'wizard/asset_sale_wizard_view.xml',
        'wizard/asset_depreciation_wizard_view.xml',
        'wizard/asset_depreciation_flag_wizard_view.xml',
        'wizard/asset_confirm_wizard_views.xml',
        'wizard/asset_filter_wizard_view.xml',
        'views/account_asset_disposal_view.xml',
        'views/account_asset_sale_view.xml',
        'views/account_asset_views.xml',
        'views/account_asset_type_view.xml',
        'views/account_invoice_line.xml',
        'views/account_move_view.xml',
        'views/account_asset_depreciation_history_view.xml',
        'views/account_config.xml',
    ],
    'installable': True,
    'application': True,
}
