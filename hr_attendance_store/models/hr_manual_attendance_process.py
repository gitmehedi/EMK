from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class HrManualAttendanceProcess(models.Model):
    _name = 'hr.manual.attendance.process'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "Import File"
    _rec_name = 'code'
    _order = 'id desc'

    code = fields.Char(string='Code', track_visibility='onchange', readonly=True)
    date = fields.Date(string='Date', default=fields.Datetime.now, track_visibility='onchange')
    line_ids = fields.One2many('hr.manual.attendance.process.line', 'line_id', string="Attendance")

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'processed':
                raise ValidationError(_('Processed record can not be deleted.'))
        return super(HrManualAttendanceProcess, self).unlink()


class HrManualAttendanceProcessLine(models.Model):
    _name = 'hr.manual.attendance.process.line'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _rec_name = 'date'
    _order = 'id desc'

    date = fields.Date(string='Date', default=fields.Datetime.now, track_visibility='onchange')
    time = fields.Char(string='Time', track_visibility='onchange')
    result = fields.Char(string='Result', track_visibility='onchange')
    mode = fields.Char(string='Mode', track_visibility='onchange')
    type = fields.Char(string='Type', track_visibility='onchange')
    card_serial_id = fields.Many2one("hr.attendance.card", string='Card Serial No', track_visibility='onchange')
    terminal_id = fields.Many2one('hr.attendance.terminal', string='Terminal ID', track_visibility='onchange')
    employee_id = fields.Many2one("hr.employee", string='Employee ID', track_visibility='onchange')
    line_id = fields.Many2one('hr.manual.attendance.process', ondelete='cascade')
