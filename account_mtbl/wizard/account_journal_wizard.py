from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountJournalWizard(models.TransientModel):
    _name = 'account.journal.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')
    default_debit_account_id = fields.Many2one('account.account', string='Debit Account',
                                               help='Default Debit Account of the Payment')
    default_credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                                help='Default Credit Account of the Payment')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['account.journal'].search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['account.journal'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.account.journal'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.account.journal'].create(
            {'change_name': self.name, 'default_debit_account_id':self.default_debit_account_id.id,
             'default_credit_account_id':self.default_credit_account_id.id,
             'status': self.status, 'request_date': fields.Datetime.now(), 'line_id': id})
        record = self.env['account.journal'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True,'maker_id': self.env.user.id})
