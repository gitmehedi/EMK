# -*- coding: utf-8 -*-
# ©  2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Holidays',
    'version': '1.0',
    'sequence': 30,
    'category': 'Human Resources',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "Manage All kinds of Holidays",
    'depends': [
        'hr',
        'hr_holidays',
        'hr_payroll',
        'gbs_hr_calendar',
        
    ],
    'data': [
#         'security/ir.model.access.csv',
#         'security/ir_rule.xml',
        'wizard/hr_calendar_clone_wizard_view.xml',
        'wizard/hr_holidays_exception_wizard_view.xml',
        'views/hr_public_holidays_view.xml',
        'views/hr_holidays_calendar_view.xml',
        'views/hr_holidays_exception_employee_batch_view.xml',
    ],
    'installable': True,
    'application': True,
}
