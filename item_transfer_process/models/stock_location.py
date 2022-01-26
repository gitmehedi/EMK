from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    can_operating_unit_transfer = fields.Boolean('Can transfer Item to Operating Unit ?')
