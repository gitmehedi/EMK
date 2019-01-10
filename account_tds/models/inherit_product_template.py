from odoo import fields, models


class InheritedProductTemplate(models.Model):
    _inherit = 'product.template'

    account_tds_id = fields.Many2one('tds.rule',string = "TDS Rule")
