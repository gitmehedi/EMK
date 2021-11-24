from odoo import api, fields, models, _


class ConfirmationMessageWizard(models.TransientModel):
    _name = 'confirmation.wizard'

    message = fields.Text('Message')

    move_id = fields.Many2one('account.move', string='Account Move')

    def action_no(self):
        move = self.env['account.move'].browse(self._context['created_move_id'])
        move.unlink()
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}

    def action_yes(self):
        move = self.env['account.move'].browse(self._context['created_move_id'])

        if move:
            payslip_run_obj = self.env['hr.payslip.run'].browse(self._context['payslip_run_id'])
            payslip_run_obj.write({'account_move_id': move.id})
            message_id = self.env['success.wizard'].create({'message': _(
                "Journal Entry Created Successfully!")
            })
            vals = {
                'payslip_run_id': self.payslip_run_id.id
            }
            return {
                'name': _('Success'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'success.wizard',
                'context': vals,
                'res_id': message_id.id,
                'target': 'new'
            }

        return {'type': 'ir.actions.act_window_close'}
