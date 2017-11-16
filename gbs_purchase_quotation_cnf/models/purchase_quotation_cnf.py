# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseCNFQuotation(models.Model):
    _inherit = 'purchase.order'

    quotation_type = fields.Char(string='Type')

    shipment_id = fields.Many2one('purchase.shipment',string='Shipment')

