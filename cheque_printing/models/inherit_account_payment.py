from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritAccountPayment(models.Model):
    _inherit='account.payment'

    cheque_info_id = fields.Many2one('cheque.info.entry', string='Cheque No', domain=[('state', '=', 'print')])


    @api.constrains('cheque_info_id')
    def _check_same_supplier(self):

        if self.partner_type == 'vendor':
            if self.cheque_info_id.partner_id == self.partner_id:
                raise ValidationError('Supplier of Cheque and Payment section should be same')

