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


class StockInventoryWizard(models.TransientModel):
    _name = 'stock.inventory.wizard'

    date_from = fields.Date("Date from", required=True)
    date_to = fields.Date("Date to", required=True)
    shop_id = fields.Many2one('operating.unit', string='Shop Name', required=True)
    category_id = fields.Many2one('product.category', string='Category', required=False)
    report_type_ids = fields.Many2many('report.type.selection', string="Report Type")

    _defaults = {
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
    }

    @api.multi
    def report_print(self):
        location = self.env['stock.location'].search([('operating_unit_id', '=', self.shop_id.id)])
        report_type = [val.code for val in self.env['report.type.selection'].search([])]
        selected_type = [val.code for val in self.report_type_ids]

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['shop_id'] = location.id
        data['shop_name'] = self.shop_id.name
        data['category_id'] = self.category_id.id
        data['report_type'] = selected_type if len(selected_type) > 0 else report_type

        return self.env['report'].get_action(self, 'category_stock_summary_reports.stock_inventory_report_qweb',
                                             data=data)
