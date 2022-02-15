from odoo import models, fields, api, _
from odoo.addons.hr_attendance_store.helpers import helper
from odoo.addons.opa_utility.helper.utility import Utility
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


class HRAttendanceCard(models.Model):
    _name = 'hr.attendance.card'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "HR Attendance Terminal"
    _rec_name = 'serial_no'
    _order = 'id desc'

    code = fields.Char(string='Code', track_visibility='onchange', required=True)
    serial_no = fields.Char(string="Card No", track_visibility='onchange', required=True)
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange')
    state = fields.Selection(helper.master_state, default='draft',
                             string='Status', track_visibility='onchange', )


    @api.constrains('name')
    def _check_name(self):
        serial_no = self.search([('serial_no', '=ilike', self.serial_no.strip()), ('state', '!=', 'reject'),
                                 '|', ('active', '=', True), ('active', '=', False)])
        if len(serial_no) > 1:
            raise ValidationError(_(Utility.UNIQUE_WARNING))

        code = self.search([('code', '=ilike', self.code.strip()), ('state', '!=', 'reject'),
                            '|', ('active', '=', True), ('active', '=', False)])
        if len(code) > 1:
            raise ValidationError(_(Utility.UNIQUE_WARNING))

    @api.onchange("name")
    def onchange_strips(self):
        if self.code:
            self.code = self.code.strip()

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
                return super(HRAttendanceCard, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Utility.UNLINK_INT_WARNING))

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('draft', 'approve', 'reject'))]
