import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, frozendict

class ConfirmItemReceiveWizard(models.TransientModel):
    _name = 'confirm.item.receive.wizard'
    _description = 'Confirm Item Receive'

    def _default_item_borrowing_id(self):
        item_borrowing_id = self.env['item.borrowing'].browse(self.env.context.get(
            'active_id'))
        return item_borrowing_id

    item_borrowing_id = fields.Many2one(
        'item.borrowing',
        default=lambda self: self._default_item_borrowing_id(),
        string='Borrowing',
        required=True
    )

    receive_date = fields.Datetime('Receive Date', track_visibility='onchange', required=True)

    @api.multi
    def confirm(self):
        if not self.item_borrowing_id.suspend_security().item_transfer_send_id.picking_id.state == 'done':
            raise UserError(_('You cannot confirm this because item sender has not completed stock picking operation.'))

        for loan in self.item_borrowing_id:
            if not loan.item_lines:
                raise UserError(_('You cannot confirm this without product.'))
            res = {
                'state': 'waiting_approval',
            }
            requested_date = datetime.strptime(self.item_borrowing_id.request_date, "%Y-%m-%d %H:%M:%S").date()

            new_seq = self.env['ir.sequence'].next_by_code_new('item.borrowing.receive', requested_date)
            if new_seq:
                res['name'] = new_seq
                res['receive_date'] = self.receive_date
            loan.write(res)
            loan.item_lines.write({'state': 'waiting_approval'})
