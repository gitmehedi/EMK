from odoo import api, fields, models,_

class OperatingUnitCurrency(models.Model):
    _inherit = 'operating.unit'
    _order= 'name desc'

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
