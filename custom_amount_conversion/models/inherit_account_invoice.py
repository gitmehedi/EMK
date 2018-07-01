from odoo import models, fields, api


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # This should be a computed field so that value won't store to DB.
    # This value will have to fetch from Sale Order section
    converstion_rate = fields.Float(string='Conversion Rate')

    @api.multi
    def action_invoice_open(self):
        res = super(InheritAccountInvoice, self).action_invoice_open()

        so_obj = self.env['sale.order'].search([('name','=',self.origin)])

        new_rate = 0

        if so_obj.currency_conversion_rate !=0:
            so_obj.currency_conversion_rate = self.converstion_rate
            new_rate = so_obj.currency_conversion_rate
        else:
            if self.converstion_rate != 0:
                currency_pool = self.env['res.currency'].search([('id', '=', self.company_id.currency_id.id)])
                currency_pool.rate = self.converstion_rate
                new_rate = currency_pool.rate

        return new_rate
