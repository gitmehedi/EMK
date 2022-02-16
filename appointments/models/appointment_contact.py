from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError
from odoo.addons.opa_utility.helper.utility import Utility


class AppointmentContact(models.Model):
    _name = 'appointment.contact'
    _description = "Appointment Contact"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    name = fields.Char(string="Appointment Title", required=True, translate=True, track_visibility='onchange')
    appointee_id = fields.Many2one('hr.employee', string="Employee", required=True, track_visibility='onchange')
    description = fields.Text('Remarks', track_visibility="onchange")
    status = fields.Boolean(default=True, track_visibility='onchange')
    topics_ids = fields.Many2many('appointment.topics', 'contact_topics_relation', 'contact_id', 'topics_id',
                                  string='Appointment Topics', track_visibility='onchange')
    timeslot_ids = fields.Many2many('appointment.timeslot', 'contact_timeslot_relation', 'timeslot_id', 'contact_id',
                                    string="Time Slot", required=True, track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search(
            [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
             ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Utility.UNIQUE_WARNING))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.onchange("appointee_id")
    def onchange_appointee(self):
        if self.appointee_id:
            self.name = '[%s] %s ' % (self.appointee_id.department_id.name, self.appointee_id.name)

    @api.constrains('appointee_id')
    def _check_appointee(self):
        appointee = self.search_count([('appointee_id', '=', self.appointee_id.id)])
        if appointee > 1:
            raise ValidationError(_('[DUPLICATE] Employee already exist, choose another.'))

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Utility.UNLINK_WARNING))
            try:
                return super(AppointmentContact, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Utility.UNLINK_INT_WARNING))


class AppointmentEmp(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def name_get(self):
        name = self.name
        if self.employee_number:
            name = '[%s] %s (%s)' % (self.employee_number, self.name, self.department_id.name)
        return self.id, name
