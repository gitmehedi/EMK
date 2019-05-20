from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ResPartnerWizard(models.TransientModel):
    _name = 'res.partner.wizard'

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
    website = fields.Char(string='Website')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    bank_ids = fields.One2many('res.partner.bank', 'partner_id', string='Banks')



    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['res.partner'].search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')


    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['res.partner'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.res.partner'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.res.partner'].create(
            {'change_name': self.name,'status': self.status,'website': self.website,'phone': self.phone,
             'mobile': self.mobile,'email': self.email,'street': self.street,'street2': self.street2,
             'zip': self.zip,'city': self.city,'state_id': self.state_id.id,'country_id': self.country_id.id,
             'bank_ids': [i.acc_number for i in self.bank_ids],'request_date': fields.Datetime.now(),
             'line_id': id})
        record = self.env['res.partner'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True})