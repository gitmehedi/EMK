from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRFQ(models.Model):
    _inherit = "purchase.rfq"

