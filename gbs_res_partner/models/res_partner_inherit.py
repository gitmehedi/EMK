from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_receivable_id = fields.Many2one(required=False)
    property_account_payable_id = fields.Many2one(required=False)