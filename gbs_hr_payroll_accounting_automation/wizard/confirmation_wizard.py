from odoo import api, fields, models, _


class ConfirmationMessageWizard(models.TransientModel):
    _name = 'confirmation.wizard'

    message = fields.Text('Message')

    move_id = fields.Many2one('account.move', string='Account Move')

    def action_no(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}

    def action_yes(self):
        vals = {
            'name': self._context['name'],
            'journal_id': self._context['journal_id'],
            'operating_unit_id': self._context['operating_unit_id'],
            'date': self._context['date'],
            'company_id': self._context['company_id'],
            'state': self._context['state'],
            'line_ids': self._context['line_ids'],
            'payslip_run_id': self._context['payslip_run_id'],
            'narration': self._context['narration'],
            'ref': self._context['ref']
        }

        move = self.env['account.move'].create(vals)

        if move:
            payslip_run_obj = self.env['hr.payslip.run'].browse(self._context['payslip_run_id'])
            payslip_run_obj.write({'account_move_id': move.id})
            message_id = self.env['success.wizard'].create({'message': _(
                "Journal Entry Created Successfully!")
            })
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
