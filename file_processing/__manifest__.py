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
    ],
    "data": [
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "security/ir.model.access.csv",
        "view/server_file_process_view.xml",
        "view/server_file_error_view.xml",
    ],
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": ["pysftp"],
    },
}
