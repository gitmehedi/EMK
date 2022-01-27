from odoo import models, fields, api, _
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.template'

    # service_type = fields.Selection([('card', 'Card'), ('copy', 'Copy'), ('event_fee', 'Event Fee')], default=False)
