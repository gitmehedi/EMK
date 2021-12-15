import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class AppointmentTopics(models.Model):
    _name = 'appointment.topics'
    _description = "Appointment Topics"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string='Topics Name', required=True, track_visibility="onchange")
    contact_ids = fields.Many2many('appointment.contact','contact_topics_relation','topics_id','contact_id' ,string='Appointment Person')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Approved')
    ], string='State', default='draft', readonly=True, copy=False, index=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise ValidationError(_('[DUPLICATE] Name already exist, choose another.'))


    def unlink(self):
        for rec in self:
            contact = self.env['appointment.appointment'].search([('topic_id', '=', rec.id)])
            if contact:
                raise ValidationError(
                    _('[Warning] You cannot delete this topics. you may be trying to delete a record while other records still reference it'))

        return super(AppointmentTopics, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', 'True')]