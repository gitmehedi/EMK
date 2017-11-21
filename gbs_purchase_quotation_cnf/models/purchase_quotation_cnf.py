# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class PurchaseCNFQuotation(models.Model):
    _name = 'cnf.quotation'
    _inherit = ['purchase.order','mail.thread', 'ir.needaction_mixin']

    quotation_type = fields.Char(string='Type')
    shipment_id = fields.Many2one('purchase.shipment',string='Shipment',required=True)
    lc_id = fields.Many2one('letter.credit',string='LC Name',required=True)
    description = fields.Text(string='Description')

    cnf_product_line = fields.One2many('cnf.quotation.line', 'cnf_quotation_id', string='Services', copy=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')], string='State',
        readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.onchange('shipment_id')
    def _onchange_shipment_id(self):
        self.lc_id = self.shipment_id.lc_id.id
        self.cnf_product_line = []
        vals = []
        for obj in self.shipment_id.shipment_product_lines:
            vals.append((0, 0, {'product_id': obj.product_id,
                                }))
        self.cnf_product_line = vals

    @api.multi
    def action_confirm(self):
        for cnf in self:
            if not cnf.cnf_product_line:
                raise UserError(_('You cannot confirm which has no line.'))
            res = {
                'state': 'confirm'
            }
            new_seq = self.env['ir.sequence'].next_by_code('cnf.quotation')
            if new_seq:
                res['name'] = new_seq

            cnf.write(res)


class PurchaseCNFQuotationLine(models.Model):
    _name = 'cnf.quotation.line'

    cnf_quotation_id = fields.Many2one('cnf.quotation', string='CNF Quotation ID')
    product_id = fields.Many2one('product.product', string='Service',
                                 required=True)
    # domain = [('type', '=', 'service')],
    amount = fields.Float(string='Amount')
    remarks = fields.Text(string='Remarks')


