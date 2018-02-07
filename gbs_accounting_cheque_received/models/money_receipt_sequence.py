from odoo import models, fields, api


class MoneyReceiptSequence(models.Model):
    _name = 'account.money.receipt'
    _rec_name = 'name'

    name = fields.Char(string='Name', readonly=True)
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/' and vals.get('id'):
            sale_type = self.env['account.money.receipt'].browse(vals['id'])
            if sale_type.sequence_id:
                vals['name'] = sale_type.sequence_id.next_by_id()
        return super(MoneyReceiptSequence, self).create(vals)
