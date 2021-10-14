from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ReceiveOutstandingAdvance(models.Model):
    _inherit = 'receive.outstanding.advance'

    debit_operating_unit_id = fields.Many2one('operating.unit', string='Debit Branch', readonly=True, required=True,
                                              track_visibility='onchange', states={'draft': [('readonly', False)]})

    def get_debit_item_data(self):
        res = super(ReceiveOutstandingAdvance, self).get_debit_item_data()
        if self.debit_operating_unit_id:
            res['operating_unit_id'] = self.debit_operating_unit_id.id
        else:
            raise ValidationError('Please select Debit Branch First')
        return res

    def get_advance_credit_item(self, advance_line):
        res = super(ReceiveOutstandingAdvance, self).get_advance_credit_item(advance_line)
        if advance_line.advance_id.operating_unit_id:
            res['operating_unit_id'] = advance_line.advance_id.operating_unit_id.id
        return res

    def create_account_move(self, journal_id):
        move = super(ReceiveOutstandingAdvance, self).create_account_move(journal_id)
        if journal_id.operating_unit_id:
            move.write({'operating_unit_id': journal_id.operating_unit_id.id})
        return move

