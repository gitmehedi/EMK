# -*- coding: utf-8 -*-

{
    "name": "GBS Data Migration",
    "summary": "GBS Data Migration",
    "version": "10.0.0.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'license': "AGPL-3",
    "category": "Tools",
    "depends": [
        'mail',
        'account',
        'mtbl_access',
        'gbs_ogl_cbs_interface',
    ],
    "data": [
        "data/ir_cron.xml",
        "views/menu_view.xml",
        "wizards/gbs_data_migration_wizard_view.xml",
        "wizards/gbs_fam_data_migration_wizard_view.xml",
        "wizards/gbs_coa_data_migration_wizard_view.xml",
        "wizards/gbs_va_data_migration_wizard_view.xml",
        "wizards/gbs_rent_data_migration_wizard_view.xml",
        "wizards/gbs_vsd_data_migration_wizard_view.xml",
        "views/gbs_fam_data_migration_view.xml",
        "views/gbs_data_migration_view.xml",
        "views/gbs_coa_data_migration_view.xml",
        "views/gbs_va_data_migration_view.xml",
        "views/gbs_rent_data_migration_view.xml",
        "views/gbs_vsd_data_migration_view.xml",
    ],
    "application": True,
    "installable": True,
}
