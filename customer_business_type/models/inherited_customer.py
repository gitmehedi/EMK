from odoo import api, fields, models, _


class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    business_type = fields.Many2one('res.customer.type', string="Business Type",ondelete='restrict',
                                    default=lambda self: self.env['res.customer.type'].search([], limit=1))