from odoo import api, fields, models, _

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')
