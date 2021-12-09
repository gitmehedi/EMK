import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AppointmentContact(models.Model):
    _name = 'appointment.contact'
    _description = "Appointment Contact"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    # @api.depends('appointee_id')
    # def _compute_name(self):
    #     for rec in self:
    #         if rec.appointee_id:
    #             self.name = self.appointee_id.name

    name = fields.Char(string="Name", required=True, translate=True, track_visibility='onchange')
    appointee_id = fields.Many2one('hr.employee', string="Appointee", required=True )
    description = fields.Text('Remarks', track_visibility="onchange")
    status = fields.Boolean(default=True, track_visibility='onchange')

    @api.constrains('appointee_id')
    def _check_name(self):
        name = self.search([('appointee_id', '=ilike', self.appointee_id)])
        print(name)
        if name:
            raise ValidationError(_('[DUPLICATE] Appointee already exist, choose another.'))

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]

#
# class AppointmentContactLines(models.Model):
#     _name = 'appointment.contact.lines'
#     _description = "Appointment Contact Line"
#
#
#     appointee_contact_id = fields.Many2one('appointment.contact', string="Appointment Contact Id", required=True, ondelete='cascade',)