from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        amount_total = sum([invoice.amount_total for invoice in self.invoice_ids])
        if self.amount > amount_total:
            raise UserError(_("Amount can't be grater then {}".format(amount_total)))

        super(AccountPayment, self).post()
