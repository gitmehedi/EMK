from odoo import models, fields, api, _
from odoo.exceptions import Warning


class CurrencyRateWizard(models.TransientModel):
    _name = 'res.currency.rate.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_rate(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).rate

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    status = fields.Boolean(string='Active', default=default_status)
    rate = fields.Char(string='Requested Rate', default=default_rate)
    name = fields.Datetime(string='Requested Date', default=default_name)

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        pending = self.env['history.res.currency.rate'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.res.currency.rate'].create(
            {'change_rate': self.rate,
             'change_name': self.name,
             'status': self.status,
             'request_date': fields.Datetime.now(), 'line_id': id
             })
        record = self.env['res.currency.rate'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True,'maker_id': self.env.user.id})
