from odoo import fields, models, api


class InheritedAccountMove(models.Model):
    _inherit = 'account.move'

    submitted_from = fields.Selection([('unit', 'Unit'), ('ho', 'HO')], default='ho')
