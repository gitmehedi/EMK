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

from openerp import api, exceptions, fields, models
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round
from openerp import tools
# from openerp.exceptions import UserError
import time


class PurchaseOrderWizard(models.TransientModel):
    _name = 'purchase.order.wizard'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True, default=fields.Date.today)
    supplier_id = fields.Many2many('res.partner', string='Supplier Name')

    @api.multi
    def report_print(self):
        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        if len(self.supplier_id):
            data['supplier'] = self.supplier_id.ids
        else:
            data['supplier'] = []

        return self.env['report'].get_action(self, 'category_stock_summary_reports.purchase_order_report_qweb',
                                             data=data)
