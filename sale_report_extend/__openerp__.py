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
    'name': 'Sales Report Management',
    'version': '1.0',
    'category': 'Sales Management',
    'sequence': 14,
    'summary': 'Quotations, Sales Orders, Invoicing',
    'description': """ Manage sales Report """,
    'author': 'OpenERP SA',
    'website': 'https://www.odoo.com/page/crm',
    'depends': ['sale'],
    'data': [
        'views/inherited_res_users_views.xml',
        'report/sale_report_extend_view.xml',
        'report/sale_report_productwise_view.xml',
        'report/sale_report_customer_wise_view.xml',
        'report/sale_report_salesperson_wise_view.xml',
        'report/sale_report_category_wise_view.xml',
        'report/sale_report_monthly_view.xml',
        'report/sale_report_target_achievement_wise_view.xml',
        'report/sale_report_commitment_delay_wise_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
