import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AppointmentContact(models.Model):
    _name = 'appointment.contact'
    _description = "Appointment Contact"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string="Name", required=True, translate=True, track_visibility='onchange')
    appointee_id = fields.Many2one('hr.employee', string="Appointee", required=True)
    description = fields.Text('Remarks', track_visibility="onchange")
    status = fields.Boolean(default=True, track_visibility='onchange')
    topics_ids = fields.Many2many('appointment.topics', 'contact_topics_relation', 'contact_id', 'topics_id',
                                  string='Appointment Topics')
    timeslot_ids = fields.Many2many('appointment.timeslot', 'contact_timeslot_relation', 'timeslot_id', 'contact_id',
                                    string="Time Slot")


    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]
