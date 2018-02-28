# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class PurchaseCNFQuotation(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order']

    cnf_quotation = fields.Boolean(string='C&F',default=lambda self: self.env.context.get('cnf_quotation') or False)
    shipment_id = fields.Many2one('purchase.shipment',string='Shipment',
                                  ondelete='cascade',default=lambda self: self.env.context.get('shipment_id') or False)
    lc_id = fields.Many2one('letter.credit',string='LC Name',ondelete = 'cascade',related = 'shipment_id.lc_id')

    partner_id = fields.Many2one('res.partner', string='C&amp;F Vendor', required=True, track_visibility='always',
                                 default=lambda self: self.env.context.get('partner_id') or False)

    @api.multi
    def button_approve(self):
        for cnf in self:
            if cnf.cnf_quotation:
                if self.state != 'draft':
                    self.shipment_id.write({'state': 'approve_cnf_quotation'})
                super(PurchaseCNFQuotation, self).button_approve()
            else:
                super(PurchaseCNFQuotation, self).button_approve()