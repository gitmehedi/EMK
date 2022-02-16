from odoo import models, fields, api, _
from odoo.addons.hr_attendance_store.helpers import helper
from odoo.addons.opa_utility.helper.utility import Utility,Message
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


class HRAttendanceTerminal(models.Model):
    _name = 'hr.attendance.terminal'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "HR Attendance Terminal"
    _rec_name = 'code'
    _order = 'id desc'

    name = fields.Char(string='Name', track_visibility='onchange', required=True)
    code = fields.Char(string='Code', track_visibility='onchange', required=True)
    device_type = fields.Selection(helper.device_type, string='Device Types', track_visibility='onchange',
                                   required=True)
    is_attendance = fields.Boolean(string="Is Attendance", default=False, track_visibility='onchange')
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'),
                            '|', ('active', '=', True), ('active', '=', False)])
        if len(name) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

        code = self.search([('code', '=ilike', self.code.strip()), ('state', '!=', 'reject'),
                            '|', ('active', '=', True), ('active', '=', False)])
        if len(code) > 1:
            raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

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
                raise ValidationError(_(Message.UNLINK_WARNING))
            try:
                return super(HRAttendanceTerminal, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]

    @api.one
    def name_get(self):
        if self.code:
            name = '%s : %s' % (self.code, self.name)
        return self.id, name
