from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError,ValidationError

class TdsVatChallan(models.Model):
    _inherit = 'tds.vat.challan'

    challan_date = fields.Date(string='Challan Date', track_visibility='onchange', required=True, readonly=True,
                               states={'draft': [('readonly', False)]},
                               default=lambda self:self.env.user.company_id.batch_date, help="Challan date")