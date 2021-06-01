# imports of python library
import datetime

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AddHonouredDateWizard(models.TransientModel):
    _name = 'add.honoured.date.wizard'

    honoured_date = fields.Date(string='Honoured Date', required=True)
    sale_order_ids = fields.Many2many('sale.order', string='Sale Order')

    @api.constrains('honoured_date')
    def _check_honoured_date(self):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        cheque_received_id = self.env.context.get('active_id')
        cheque_received = self.env['accounting.cheque.received'].search([('id', '=', cheque_received_id)])
        if cheque_received.date_on_cheque > self.honoured_date:
            raise ValidationError(_('Honoured date must be greater than Date On Cheque'))
        if self.honoured_date > current_date:
            raise ValidationError(_('Honoured date can not be greater than today'))

    @api.one
    def action_proceed(self):
        cheque_received_id = self.env.context.get('active_id')
        cheque_received = self.env['accounting.cheque.received'].search([('id', '=', cheque_received_id)])
        cheque_received.write({
            'honoured_date': self.honoured_date,
            'sale_order_id': [(6, 0, self.sale_order_ids.ids)]
        })
