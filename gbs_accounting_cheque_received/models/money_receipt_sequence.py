from odoo import models, fields, api


class MoneyReceiptSequence(models.Model):
    _name = 'account.money.receipt'

    name = fields.Char(string='Name', readonly=True)
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', copy=False)

    @api.model
    def create(self, vals):
        seq = self.sequence_id.next_by_code('account.money.receipt') or '/'
        vals['name'] = seq

        return super(MoneyReceiptSequence, self).create(vals)
