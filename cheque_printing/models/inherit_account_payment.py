from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritAccountPayment(models.Model):
    _inherit='account.payment'

    cheque_info_id = fields.Many2one('cheque.info.entry', string='Cheque No', domain=[('state', '=', 'print')])


    @api.onchange('cheque_info_id')
    def _onchange_cheque_info(self):

        if self.partner_type == 'supplier':
            if self.cheque_info_id.partner_id.id != self.partner_id.id:
                raise ValidationError('Supplier of Cheque No. and Payment section must be same')

        self.amount = self.cheque_info_id.amount
        self.partner_id = self.cheque_info_id.partner_id






