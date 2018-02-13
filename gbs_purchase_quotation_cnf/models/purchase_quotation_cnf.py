# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class PurchaseCNFQuotation(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order']

    cnf_quotation = fields.Boolean(string='C&F',default=False)
    shipment_id = fields.Many2one('purchase.shipment',string='Shipment', ondelete='cascade')
    lc_id = fields.Many2one('letter.credit',string='LC Name',ondelete = 'cascade',related = 'shipment_id.lc_id')

    # @api.multi
    # def action_confirm(self):
    #     for cnf in self:
    #         if not cnf.cnf_product_line:
    #             raise UserError(_('You cannot confirm which has no Service.'))
    #
    #         res = {
    #             'state': 'confirm'
    #         }
    #         self.shipment_id.write({'state': 'cnf_quotation'})
    #         new_seq = self.env['ir.sequence'].next_by_code('cnf.quotation')
    #         if new_seq:
    #             res['name'] = new_seq
    #
    #         cnf.write(res)
    #
    # @api.multi
    # def action_approve(self):
    #     for cnf in self:
    #         res = {
    #             'state': 'approved'
    #         }
    #         self.shipment_id.write({'state': 'approve_cnf_quotation'})
    #         cnf.write(res)

# default=lambda self: self.env.context.get('shipment_id')
# default=lambda self: self.env.context.get('lc_id')