from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AppointmentContact(models.Model):
    _name = 'appointment.contact'
    _description = "Appointment Contact"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string="Title", required=True, translate=True, track_visibility='onchange')
    appointee_id = fields.Many2one('hr.employee', string="Employee", required=True, track_visibility='onchange')
    description = fields.Text('Remarks', track_visibility="onchange")
    status = fields.Boolean(default=True, track_visibility='onchange')
    topics_ids = fields.Many2many('appointment.topics', 'contact_topics_relation', 'contact_id', 'topics_id',
                                  string='Appointment Topics', track_visibility='onchange')
    timeslot_ids = fields.Many2many('appointment.timeslot', 'contact_timeslot_relation', 'timeslot_id', 'contact_id',
                                    string="Time Slot", required=True, track_visibility='onchange')


    def unlink(self):
        for rec in self:
            contact = self.env['appointment.appointment'].search([('contact_id', '=', rec.id)])
            if contact:
                raise ValidationError(
                    _('[Warning] You cannot delete this contact. you may be trying to delete a record while other records still reference it'))

        return super(AppointmentContact, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]


class AppointmentEmp(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def name_get(self):
        name = self.name
        if self.employee_number:
            name = '[%s] %s' % (self.employee_number, self.name)
        return (self.id, name)

