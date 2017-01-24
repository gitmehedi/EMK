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

import time

from openerp import api, exceptions, fields, models

class PebblesAccountInvoiceWizard(models.TransientModel):

    """Refunds invoice"""
    _name = "pebbles.account.invoice.wizard"

    product_id = fields.Many2one('product.product', 'Product Name')
    partner_id = fields.Many2one('res.partner', 'Partner Name')
    category_id = fields.Many2one('product.category', 'Category of Product')



    @api.multi
    def invoice_create(self):

        context = {
            'product_id': self.product_id.id,
            'partner_id': self.partner_id.id,
            'category_id': self.category_id.id
        }
        print "----------------context----------", context
        return {
            'view_type': 'graph',
            'view_mode': 'graph',
            'res_model': 'pebbles.account.invoice.report',
            'view_id': False,
            'type': 'ir.actions.act_window',

            'context': context,
        }


