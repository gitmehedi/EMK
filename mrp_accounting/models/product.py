# imports of odoo
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    raw_cogs_account_id = fields.Many2one('account.account', string="COGS Account (RM)")
    packing_cogs_account_id = fields.Many2one('account.account', string="COGS Account (PM)")
