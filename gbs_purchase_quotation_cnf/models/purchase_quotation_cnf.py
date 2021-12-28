# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError

class PurchaseCNFQuotation(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order']

    cnf_quotation = fields.Boolean(string='C&F',default=lambda self: self.env.context.get('cnf_quotation') or False)
    shipment_id = fields.Many2one('purchase.shipment',string='Shipment',
                                  ondelete='cascade',default=lambda self: self.env.context.get('shipment_id') or False)
    lc_id = fields.Many2one('letter.credit',string='LC Name',ondelete = 'cascade',related = 'shipment_id.lc_id')

    commodity = fields.Char('Commodity', help="Commodity rating")
    com_quantity = fields.Char('Quantity', help="Quantity")

    @api.onchange('shipment_id')
    def onchange_shipment_id(self):
        if self.shipment_id:
            self.partner_id = self.shipment_id.cnf_id.id
            self.operating_unit_id = self.shipment_id.lc_id.operating_unit_id.id
            stock_warehouse = self.env['stock.warehouse'].sudo().search(
                [('operating_unit_id', '=', self.operating_unit_id.id)],
                limit=1
            )
            if stock_warehouse and stock_warehouse.in_type_id:
                self.picking_type_id = stock_warehouse.in_type_id.id

    @api.model
    def create(self, vals):
        # set operating unit in vals
        shipment = self.env['purchase.shipment'].search([('id', '=', vals.get('shipment_id'))])
        vals['operating_unit_id'] = shipment.lc_id.operating_unit_id.id

        if vals.get('cnf_quotation'):
            vals['name'] = self.env['ir.sequence'].next_by_code_new('cnf.quotation', datetime.today(), shipment.lc_id.operating_unit_id) or '/'

        return super(PurchaseCNFQuotation, self).create(vals)

    @api.multi
    def cnf_button_confirm(self):
        for cnf in self:
            if cnf.cnf_quotation:
                return super(PurchaseCNFQuotation, self).button_approve()

    def action_reset_cnf(self):
        if self.shipment_id.state in ['done','cancel']:
            raise UserError(_('Sorry! Unable to reverse this C&F because the shipment is done.'))
        self.write({'state': 'draft'})