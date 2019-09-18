# -*- coding: utf-8 -*-

{
    "name": "GBS OGL-CBS Interface",
    "summary": "OGL CBS Interface",
    "version": "10.0.0.0.0",
    'author': 'Genweb2 Limited',
    'website': 'http://www.genweb2.com',
    'license': "AGPL-3",
    "category": "Tools",
    "depends": [
        'mail',
        'account',
        'gbs_payment_instruction',
        'gbs_vendor_bill',
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/default_data.xml",
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "views/menu_view.xml",
        "views/glif_process_view.xml",
        "views/glif_process_error_view.xml",
        "views/glif_process_success_view.xml",
        "views/api_process_view.xml",
        "views/api_process_error_view.xml",
        "views/cbs_batch_process_success_view.xml",
        "views/cbs_batch_process_view.xml",
        "views/payment_instruction_view.xml",
    ],
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": ["pysftp"],
    },
}
