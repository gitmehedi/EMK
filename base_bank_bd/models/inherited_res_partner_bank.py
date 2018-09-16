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
    is_company_account = fields.Boolean('Company Account', default=False)

    @api.multi
    def name_get(self):

        result = []
        for record in self:
            name = record.acc_number
            if record.bank_id and record.currency_id:
                name = name + ' ('+record.bank_id.bic+' - ' + record.currency_id.name + ')'
            result.append((record.id, name))
        return result