# -*- coding: utf-8 -*-
{
    'name': 'Samuda Commission Refund Slab',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Sales',
    'version': '10.0.1.0.0',
    'sequence': 14,
    'depends': [
        'base',
        'account',
        'gbs_commission_refund',
        'gbs_commission_config'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_journal_data.xml',
        'data/ir_cron.xml',
        'data/sequence.xml',
        'views/comm_refund_prcntg_config_views.xml',
        'views/inherited_sale_config_settings.xml'

    ],
    'summary': 'Override base module logic.',
    'description': """""",
    'installable': True,
    'application': False,
}
