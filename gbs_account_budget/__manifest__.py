{
    'name': 'Budget Management',
    'author': 'Genweb2 Limited',
    'version': '10.0.0.1',
    'category': 'Accounting',
    'summary': 'Custom Budget Management',
    'description': """
This module allows accountants to manage branch,analytic and crossovered budgets.
==========================================================================

Once the Budgets are defined, the Project Managers
can set the planned amount on each Branch.

The accountant has the possibility to see the total of amount planned for each
Budget in order to ensure the total planned is not greater/lower than what he
planned for this Budget.

""",
    'depends': [
        'account',
        'operating_unit',
        'date_range',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'security/ir_security.xml',
        # 'security/ir_rule.xml',
        'wizards/budget_account_wizard.xml',
        'views/bottom_line_budget_views.xml',
        'views/budget_distribution_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}