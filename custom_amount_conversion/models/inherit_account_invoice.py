from odoo import models, fields, api


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # This should be a computed field so that value won't store to DB.
    # This value will have to fetch from Sale Order section
    converstion_rate = fields.Float(string='Conversion Rate', store=False)

    @api.multi
    def action_invoice_open(self):
        res = super(InheritAccountInvoice, self).action_invoice_open()
        currency_pool = self.env['res.currency.rate'].search([('currency_id', '=', self.company_id.currency_id.id)])

        if self.converstion_rate != 0:
            currency_pool.rate = self.converstion_rate

        res = currency_pool.rate
        return res
