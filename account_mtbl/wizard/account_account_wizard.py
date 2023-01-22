from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountAccountWizard(models.TransientModel):
    _name = 'account.account.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_reconcile(self):
        context = self._context
        record = self.env[context['active_model']].search([('id', '=', context['active_id'])])
        if record:
            return record.reconcile
        else:
            return True

    @api.model
    def default_originating_type(self):
        context = self._context
        record = self.env[context['active_model']].search([('id', '=', context['active_id'])])
        if record:
            return record.originating_type
        else:
            return False

    @api.model
    def default_status(self):
        context = self._context
        record = self.env[context['active_model']].search([('id', '=', context['active_id'])])
        if record:
            return record.active
        else:
            return True

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')
    user_type_id = fields.Many2one('account.account.type', string='Type')
    currency_id = fields.Many2one('res.currency', string='Account Currency')
    tpm_currency_id = fields.Many2one('res.currency', string='TPM Currency')
    reconcile = fields.Boolean(string='Allow Reconciliation', default=default_reconcile)
    originating_type = fields.Selection([('debit', 'Originating Debit'), ('credit', 'Originating Credit')],
                                        string='Originating Type', default=default_originating_type)

    @api.onchange('reconcile')
    def onchange_originating_type(self):
        if not self.reconcile:
            self.originating_type = False

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['account.account'].search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['account.account'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        if not self.status:
            aml = self.env['account.move.line'].search([('account_id', '=', id)])
            if len(aml) > 0:
                raise Warning('[Warning] Already have Journal!')

        pending = self.env['history.account.account'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.account.account'].create({'change_name': self.name,
                                                    'currency_id': self.currency_id.id,
                                                    'tpm_currency_id': self.tpm_currency_id.id,
                                                    'user_type_id': self.user_type_id.id,
                                                    'status': self.status,
                                                    'request_date': fields.Datetime.now(),
                                                    'line_id': id,
                                                    'reconcile': self.reconcile,
                                                    'originating_type': self.originating_type})

        record = self.env['account.account'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if not record:
            record = self.env['account.account'].with_context({'show_parent_account': True}).search(
                [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True, 'maker_id': self.env.user.id})
