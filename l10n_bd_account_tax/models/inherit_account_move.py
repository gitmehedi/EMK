from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        for record in self:
            for line in record.line_ids:
                if line.debit == 0.0 and line.credit == 0.0 and line.amount_currency == 0.0:
                    line.unlink()
        return super(AccountMove, self).post()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = "date desc, id asc"

    tax_type = fields.Selection([('vat', 'VAT'), ('tds', 'TDS')], string='VAT/TDS')
    is_tdsvat_payable = fields.Boolean('TDS/VAT Payable', default=False)