# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    code = fields.Char('Short Name', required=True, size=15,
                       help="Short name used to identify your warehouse")

    wh_main_stock_loc_id = fields.Many2one('stock.location', 'Main Location')


