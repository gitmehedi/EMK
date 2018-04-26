# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import datetime

class PurchaseCNFQuotation(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order']

    cnf_quotation = fields.Boolean(string='C&F',default=lambda self: self.env.context.get('cnf_quotation') or False)
    shipment_id = fields.Many2one('purchase.shipment',string='Shipment',
                                  ondelete='cascade',default=lambda self: self.env.context.get('shipment_id') or False)
    lc_id = fields.Many2one('letter.credit',string='LC Name',ondelete = 'cascade',related = 'shipment_id.lc_id')

    partner_id = fields.Many2one('res.partner', string='C&F Vendor', required=True, track_visibility='always',
                                 default=lambda self: self.env.context.get('partner_id') or False)

    @api.model
    def create(self, vals):
        if vals.get('cnf_quotation'):
            vals['name'] = self.env['ir.sequence'].next_by_code_new('cnf.quotation', datetime.today()) or '/'
            shipment_pool = self.env['purchase.shipment']
            shipment_obj = shipment_pool.search([('id', '=', vals['shipment_id'])])
            shipment_obj.write({'state': 'approve_cnf_quotation'})
        return super(PurchaseCNFQuotation, self).create(vals)

    @api.multi
    def cnf_button_confirm(self):
        for cnf in self:
            if cnf.cnf_quotation:
                self.shipment_id.write({'state': 'approve_cnf_quotation'})
                return super(PurchaseCNFQuotation, self).button_approve()