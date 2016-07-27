# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    ################  -------Configuration++++++++++++++++++++++
#    Go to settings -> General Settings -> Configure your company Data
#    Go to "Configuration Tab -> Levels of Approvals -> Select Radio Button: Get 2 levels of approvals to confirm a purchase order
#    Give Amount-> Double validation amount
##############################################################################

{
    'name' : 'Purchases Triple Validation',
    'version' : '0.1',
    'category': 'Purchase Management',
    'depends' : ['stock_account'],
    'author' : 'OpenERP SA',
    'description': """
Triple-validation for purchases exceeding minimum amount.
=========================================================

This module modifies the purchase workflow in order to validate purchases that
exceeds minimum amount set by configuration wizard.
    """,
    'website': 'http://www.openerp.com',
    'data': [
        'security/purchase_triple_validation_security.xml',
        'views/inherited_res_company_view.xml',
        'views/inherited_pruchase_order_view.xml'
#         'views/purchase_triple_validation_workflow.xml',
#         'views/pruchase_config_view.xml',
#         'views/pruchase_view.xml',
    ],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
