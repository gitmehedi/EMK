# -*- coding: utf-8 -*-

{
    "name": "Server File Processing",
    "summary": "Server File Processing",
    "version": "10.0.0.0.0",
    "author": "",
    'license': "AGPL-3",
    "category": "Tools",
    "depends": [
        'mail',
        'account',
    ],
    "data": [
        # "data/default_data.xml",
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "security/ir.model.access.csv",
        "views/menu_view.xml",
        "views/server_file_process_view.xml",
        "views/server_file_process_error_view.xml",
        "views/soap_process_view.xml",
        "views/soap_process_error_view.xml",
    ],
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": ["pysftp"],
    },
}
