from odoo import fields, models, api


class ConfirmationMessageWizard(models.TransientModel):
    _name = 'confirmation.wizard'

    message = fields.Text('Message')

    name = fields.Char(string='Number')
    journal_id = fields.Many2one('account.journal', string='Journal')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    date = fields.Date()
    company_id = fields.Many2one('res.company', string='Company')
    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')], string='Status')
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items')
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Run')
    narration = fields.Text(string='Internal Note')
    ref = fields.Char(string='Reference')

    def action_no(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}

    def action_yes(self):
        print('line_ids', self._context['line_ids'])

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

            # Provision above amount against Salary month of July - 2021
        }
        move = self.env['account.move'].create(vals)

        return {'type': 'ir.actions.act_window_close'}
