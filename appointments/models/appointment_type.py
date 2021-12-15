import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class AppointmentType(models.Model):
    _name = 'appointment.type'
    _description = "Appointment Type"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string='Type Name', required=True, track_visibility="onchange")
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')


    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))


    def unlink(self):
        for rec in self:
            contact = self.env['appointment.appointment'].search([('type_id', '=', rec.id)])
            if contact:
                raise ValidationError(
                    _('[Warning] You cannot delete this type. you may be trying to delete a record while other records still reference it'))

        return super(AppointmentType, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]