from datetime import datetime
from openerp import api, models, fields


class ExtendOperatingUnit(models.Model):
    _inherit = 'operating.unit'

    min_stock_days = fields.Integer(string='Minimum Stock Days', required=True)
