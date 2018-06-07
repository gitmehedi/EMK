from odoo import api, fields, models
import datetime
from odoo.exceptions import ValidationError


class ChequeInfoEntry(models.Model):
    _name = 'cheque.info.entry'
    _description = 'Cheque Info Entry'
    _rec_name = 'cheque_number'
    _inherit = ['mail.thread']

    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('supplier', '=', True)], required=True, )
    cheque_number = fields.Integer(string='Cheque No.', required=True,)
    cheque_date = fields.Date(string='Date', required=True,)
    amount = fields.Float(string='Amount', required=True, )

    is_cheque_paid = fields.Boolean(string='Is Cheque Paid', default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('print', 'Print'),
        ('cancel', 'Cancel')
    ], default='draft')

    """ All methods"""

    @api.constrains('amount')
    def _check_amount_negative_val(self):
        if self.amount < 0 :
            raise ValidationError('Amount can not be Negative')

    def action_confirm(self):
        self.state = 'confirmed'

    def action_print_approved(self):
        self.state = 'print'

    def action_cancel(self):
        self.state='cancel'


    @api.multi
    def unlink(self):
        for cheque in self:
            if cheque.state != 'draft':
                raise ValidationError('You can not delete record which is not in Draft state')
            cheque.unlink()
        return super(ChequeInfoEntry, self).unlink()

