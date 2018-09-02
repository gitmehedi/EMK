from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit = 'res.partner.bank'


    """ Relational Fields """

    bank_swift_code = fields.Char(string='Bank Swift Code')
    branch_code = fields.Char(string='Branch Code')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')