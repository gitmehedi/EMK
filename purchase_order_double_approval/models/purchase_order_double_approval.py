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

class InheritPurchaseConfigSettings(models.Model):
    _inherit = 'purchase.config.settings'
    
    min_limit_amount= fields.Integer('limit to require a second approval',required=True,
            help="Amount after which Approval of purchase is required.")
#     item_qty = fields.Integer('limit Item Quantity to require a second approval',required=True)
#     name = fields.Char(
#                 string='Name',
#                 default=_get_default_name,
#             )

    _defaults = {
        'min_limit_amount': 50,
#         'item_qty': 50,
    }
    
    @api.multi
    def get_default_limit_amount(self):
        ir_model_data = self.env['ir.model.data']
#         print '===========self+++++++',self.purchase_order_double_approval
        transition = ir_model_data.get_object('purchase_order_double_approval', 'trans_confirmed_double_lt')
        field, value = transition.condition.split('<', 1)
        return {'min_limit_amount': int(value)}
     
    @api.multi
    def set_limit_amount(self):
        ir_model_data = self.env['ir.model.data']
        config = self.browse(self.ids)
        waiting = ir_model_data.get_object('purchase_order_double_approval', 'trans_confirmed_double_gt')
        waiting.write({'condition': 'amount_total >= %s' % config.min_limit_amount})
        confirm = ir_model_data.get_object('purchase_order_double_approval', 'trans_confirmed_double_lt')
        confirm.write({'condition': 'amount_total < %s' % config.min_limit_amount})
    """
        
    def get_default_min_limit_amount(self, cr, uid, fields, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        transition = ir_model_data.get_object(cr, uid, 'purchase_order_double_approval', 'trans_confirmed_double_lt')
        field, value = transition.condition.split('<', 1)
        return {'min_limit_amount': int(value)}
       
    def set_min_limit_amount(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        config = self.browse(cr, uid, ids[0], context)
        waiting = ir_model_data.get_object(cr, uid, 'purchase_order_double_approval', 'trans_confirmed_double_gt')
        waiting.write({'condition': 'amount_total >= %s' % config.min_limit_amount})
        confirm = ir_model_data.get_object(cr, uid, 'purchase_order_double_approval', 'trans_confirmed_double_lt')
        confirm.write({'condition': 'amount_total < %s' % config.min_limit_amount})
    """
#     @api.model
#     def _get_default_name(self):
#         return "test"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
