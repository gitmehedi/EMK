from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProformaInvoice(models.Model):
    _inherit = 'proforma.invoice'

    lc_id = fields.Many2one('letter.credit', string='LC Ref. No.', track_visibility='onchange', readonly=True)


