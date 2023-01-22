from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountTypeWizard(models.TransientModel):
    _name = 'account.account.type.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    @api.model
    def default_include_initial(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).include_initial_balance

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')
    include_initial_balance = fields.Boolean(string='Bring Accounts Balance Forward', default=default_include_initial)
    type = fields.Selection([
        ('other', 'Regular'),
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
        ('liquidity', 'Liquidity'),
    ], default='other',
        help="The 'Internal Type' is used for features available on " \
             "different types of accounts: liquidity type is for cash or bank accounts" \
             ", payable/receivable is for vendor/customer accounts.")


    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['account.account.type'].search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['account.account.type'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.account.account.type'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.account.account.type'].create(
            {'change_name': self.name,
             'type':self.type,
             'status': self.status,
             'include_initial_balance': self.include_initial_balance,
             'request_date': fields.Datetime.now(),
             'line_id': id})
        record = self.env['account.account.type'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True,'maker_id': self.env.user.id})
