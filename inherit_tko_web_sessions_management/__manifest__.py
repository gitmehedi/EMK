# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Inherit Web Sessions Management',
    'summary': '',
    'description': 'Sessions timeout and forced termination. Multisession control. Login by calendar (week day hours). Remote IP filter and location.',
    'author': 'TKO',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'resource',
        'web',
        'tko_web_sessions_management',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'data': [
        'data/ir_config_parameter_data.xml'
    ],
}
