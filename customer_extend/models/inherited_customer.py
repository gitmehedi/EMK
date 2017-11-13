from openerp import models, fields, api


class InhiredResPartner(models.Model):
    _inherit = 'res.partner'

    membership_card = fields.Char(string='Membership Card', size=100)
