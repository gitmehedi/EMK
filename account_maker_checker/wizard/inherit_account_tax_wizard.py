from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountTaxWizard(models.TransientModel):
    _name = 'account.tax.wizard'

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

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['account.tax'].search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['account.tax'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.account.tax'].search([('state', '=', 'pending'), ('history_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.account.tax'].create({'change_name': self.name,
                                                'status': self.status,
                                                'request_date': fields.Datetime.now(),
                                                'history_id': id})
        record = self.env['account.tax'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True, 'maker_id': self.env.user.id})
