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
#
##############################################################################

{
    'name' : 'Double Approval Purchases Order',
    'version' : '1.0',
    'category': 'Purchase Management',
    'depends' : ['purchase'],
    'author' : 'OpenERP SA',
    'description': """
Double-Approval for purchases Order exceeding minimum amount and minimum item Quantity.
=========================================================

This module modifies the purchase workflow in order to validate purchases that
exceeds minimum amount and minimum item Quantity set by configuration wizard.
    """,
    'website': 'www.genweb2.com',
    'data': [
        'views/inherited_purchase_order.xml',
#         'views/inherited_purchase_settings.xml',
        'views/purchase_double_approval_workflow.xml',
#         'views/purchase_double_approval_installer.xml',
        'views/purchase_double_approval_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
