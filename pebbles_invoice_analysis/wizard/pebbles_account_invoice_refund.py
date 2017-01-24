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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval

class PebblesAccountInvoiceWizard(osv.osv_memory):

    """Refunds invoice"""

    _name = "pebbles.account.invoice.wizard"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product Name'),
        'partner_id': fields.many2one('res.partner', 'Partner Name'),
        'category_id': fields.many2one('product.category', 'Category of Product'),
    }



    def invoice_create(self, cr, uid, ids, context=None):


        return {
            'view_type': 'graph',
            'view_mode': 'graph',
            'src_model': 'pebbles.account.invoice.report',
            'res_model': 'pebbles.account.invoice.report',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context,
        }


