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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Validation'),
        ('validated', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]
    
    date_validate=fields.Date('Date Validated', readonly=1, select=True, help="Date on which purchase order has been approved")
    state= fields.Selection(STATE_SELECTION, 'State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True)
    
    @api.multi
    def action_validated(self):
        """ Sets state to validated.
        @return: True
        """
        self.state = "validated"
        self.date_validate = fields.Date.today()
        return True
    

class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'
    
    
    second_limit_amount= fields.Integer('limit to require a third approval',required=True,
        help="Amount after which third validation of purchase is required.")
    module_purchase_triple_validation= fields.Boolean("Force three levels of approvals",
        help="""Provide a triple validation mechanism for purchases exceeding minimum amount.
            This installs the module purchase_triple_validation.""")
    
    
    _defaults = {
        'second_limit_amount': 10000,
    }
    
    @api.multi
    def get_default_limit_amount(self, values):
        res = super(PurchaseConfigSettings, self).get_default_limit_amount(values)
        ir_model_data = self.env['ir.model.data']
        transition = ir_model_data.get_object('purchase_triple_validation', 'trans_confirmed_triple_lt')
        field, value = transition.condition.split('<', 1)
        return {'second_limit_amount': int(value)}
     
    @api.multi
    def set_limit_amount(self):
        super(PurchaseConfigSettings, self).set_limit_amount()
        ir_model_data = self.env['ir.model.data']
        config = self.browse(self.ids)
        waiting = ir_model_data.get_object('purchase_triple_validation', 'trans_confirmed_triple_gt')
        waiting.write({'condition': 'amount_total >= %s' % config.second_limit_amount})
        confirm = ir_model_data.get_object('purchase_triple_validation', 'trans_confirmed_triple_lt')
        confirm.write({'condition': 'amount_total < %s' % config.second_limit_amount})

    
PurchaseConfigSettings()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

