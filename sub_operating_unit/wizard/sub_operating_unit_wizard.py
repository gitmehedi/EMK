from odoo import models, fields, api, _
from odoo.exceptions import Warning


class SubOperatingUnitWizard(models.TransientModel):
    _name = 'sub.operating.unit.wizard'

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
            name = self.env['sub.operating.unit'].search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        # name = self.env['sub.operating.unit'].search([('name', '=', self.name), ('id', '=', id)])
        # if len(name) > 0:
        #     raise Warning('[Unique Error] Please Select another name!')

        name = self.env['sub.operating.unit'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.sub.operating.unit'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.sub.operating.unit'].create({'change_name': self.name, 'line_id': id, 'status': self.status})
        operating_unit = self.env['sub.operating.unit'].search([('id', '=', id)])
        if operating_unit:
            operating_unit.pending = True
