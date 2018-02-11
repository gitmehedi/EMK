from odoo import models, fields, api


class MoneyReceiptSequence(models.Model):
    _name = 'account.money.receipt'
    _rec_name = 'name'

    name = fields.Char(string='Name', readonly=True)
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', copy=False)

   # company_id = lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('gbs_accounting_cheque_received'))


    @api.model
    def create(self, vals):

        #print self.company_id

        seq = self.sequence_id.next_by_code('account.money.receipt') or '/'
        vals['name'] = seq

        return super(MoneyReceiptSequence, self).create(vals)
