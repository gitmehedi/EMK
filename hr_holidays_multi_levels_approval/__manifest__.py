# -*- encoding: utf-8 -*-
# Baamtu, 2017
# GNU Affero General Public License <http://www.gnu.org/licenses/>
{
    "name" : "Holidays multi levels approval",
    "version" : "10.3",
    'license': 'AGPL-3',
    "author" : "Baamtu Senegal",
    "category": "Generic Modules/Human Resources",
    'website': 'http://www.baamtu.com/',
    'images': ['static/description/banner.jpg'],
    'depends' : ['hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/custom_validation_level_wizard_view.xml',
        'views/employee.xml',
        'views/holidays.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
