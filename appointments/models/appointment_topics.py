import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class AppointmentTopics(models.Model):
    _name = 'appointment.topics'
    _description = "Appointment Topics"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string='Topics Name', required=True, track_visibility="onchange")
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]