# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
