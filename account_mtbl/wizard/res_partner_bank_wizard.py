from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ResPartnerBAnkWizard(models.TransientModel):
    _name = 'res.partner.bank.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).acc_number

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    status = fields.Boolean(string='Active', default=default_status)
    acc_number = fields.Char(string='Requested Account Number')
    bank_id = fields.Many2one('res.bank', string="Bank")

    @api.constrains('acc_number')
    def _check_unique_constrain(self):
        if self.acc_number:
            acc_number = self.env['res.partner.bank'].search(
                [('acc_number', '=ilike', self.acc_number.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(acc_number) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        if self.acc_number:
            acc_number = self.env['res.partner.bank'].search([('acc_number', '=ilike', self.acc_number)])
            if len(acc_number) > 0:
                raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.res.partner.bank'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.res.partner.bank'].create(
            {'acc_number': self.acc_number, 'bank_id':self.bank_id.id, 'status': self.status, 'request_date': fields.Datetime.now(), 'line_id': id})
        record = self.env['res.partner.bank'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True})
