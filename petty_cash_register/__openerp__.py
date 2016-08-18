# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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
    'name': 'Petty Cash Register',
    'version': '1.0',
    'category': 'Account',
    'description': """
    """,
    'author': 'Genweb2 Ltd.',
    'depends': ['base', 'account', 'base_company_branch', 'hr'],
    'data': ["security/ir.model.access.csv",
             "menu.xml",
             "views/petty_cash_disbursement_view.xml", 
             "views/iou_slip_view.xml",
             "views/iou_adjustment_view.xml",
             "sequence.xml",
             "wizard/petty_cash_wizard_view.xml",
             "report/petty_cash_report.xml",
             "report/petty_cash_report_view.xml",
             ],
    'installable': True,
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
