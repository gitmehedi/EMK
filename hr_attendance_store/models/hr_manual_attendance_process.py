from odoo import api, models, fields, _
from odoo.addons.hr_attendance_store.helpers import helper
from odoo.exceptions import ValidationError


class HrManualAttendanceProcess(models.Model):
    _name = 'hr.manual.attendance.process'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "Import File"
    _rec_name = 'date'
    _order = 'id desc'

    date = fields.Date(string='Date', default=fields.Datetime.now, track_visibility='onchange', required=True)
    attendance_filename = fields.Char(string='Attendance Filename', track_visibility='onchange')
    attendance_file = fields.Binary(string='Attendance File', attachement=True, track_visibility='onchange')
    error_filename = fields.Char(string='Error Filename', track_visibility='onchange', )
    error_file = fields.Binary(string='Error File', attachement=True, track_visibility='onchange')
    filter_ids = fields.One2many('hr.manual.attendance.process.filter', 'line_id', string="Attendance")
    line_ids = fields.One2many('hr.manual.attendance.process.line', 'line_id', string="Attendance")
    state = fields.Selection(helper.process_state, default='draft', string='State', track_visibility='onchange')

    @api.one
    def act_draft(self):
        if self.state == 'filter':
            self.state = 'draft'

    @api.one
    def act_filter(self):
        if self.state == 'draft':
            self.filter_ids.unlink()
            terminal_ids = self.env['hr.attendance.terminal'].search([('is_attendance', '=', True),
                                                                      ('active', '=', True),
                                                                      ('pending', '=', False)])
            query = """SELECT date,
                            EMPLOYEE_ID,
                            MIN(terminal_id) AS terminal_id,
                            MIN(TO_TIMESTAMP(TIME, 'HH24:MI:SS')::TIME) AS ENTRY_TIME,
                            MAX(TO_TIMESTAMP(TIME, 'HH24:MI:SS')::TIME) AS EXIT_TIME,
                            MAX(TO_TIMESTAMP(TIME, 'HH24:MI:SS')::TIME) - MIN(TO_TIMESTAMP(TIME, 'HH24:MI:SS')::TIME) AS DURATION
                        FROM HR_MANUAL_ATTENDANCE_PROCESS_LINE ATP
                        WHERE TERMINAL_ID IN %s AND LINE_ID=%s
                        GROUP BY EMPLOYEE_ID,DATE
                        ORDER BY date DESC,EMPLOYEE_ID DESC;"""
            self._cr.execute(query, [tuple(terminal_ids.ids), self.id])
            for line in self.env.cr.fetchall():
                vals = {}
                vals['date'] = line[0]
                vals['employee_id'] = line[1]
                vals['terminal_id'] = line[2]
                vals['entry_time'] = line[3]
                vals['exit_time'] = line[4]
                vals['duration'] = str(line[5])
                vals['line_id'] = self.id
                self.filter_ids.create(vals)
            self.state = 'filter'

    @api.one
    def act_approve(self):
        if self.state == 'filter':
            query = """SELECT employee_id,
                            date,
                            (date ||' '|| entry_time)::timestamp  as entry_time,
                            (date ||' '|| exit_time)::timestamp  as exit_time
                        FROM HR_MANUAL_ATTENDANCE_PROCESS_FILTER 
                        WHERE LINE_ID=%s;"""
            self._cr.execute(query, [self.id])
            for line in self.env.cr.fetchall():
                vals = {}
                vals['employee_id'] = line[0]
                vals['duty_date'] = line[1]
                vals['check_in'] = line[2]
                vals['check_out'] = line[3]
                self.env['hr.attendance'].create(vals)
            self.state = 'approve'

    @api.one
    def act_done(self):
        if self.state == 'approve':
            self.state = 'done'

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.state = 'reject'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('filter', 'approve', 'done'):
                raise ValidationError(_('Processed record can not be deleted.'))
        return super(HrManualAttendanceProcess, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('filter', 'approve', 'migrate'))]


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


class HrManualAttendanceProcessLine(models.Model):
    _name = 'hr.manual.attendance.process.filter'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _rec_name = 'date'
    _order = 'id desc'

    date = fields.Date(string='Date', default=fields.Datetime.now, track_visibility='onchange')
    entry_time = fields.Char(string='Entry Time', track_visibility='onchange')
    exit_time = fields.Char(string='Exit Time', track_visibility='onchange')
    card_serial_id = fields.Many2one("hr.attendance.card", string='Card Serial No', track_visibility='onchange')
    terminal_id = fields.Many2one('hr.attendance.terminal', string='Terminal ID', track_visibility='onchange')
    employee_id = fields.Many2one("hr.employee", string='Employee ID', track_visibility='onchange')
    duration = fields.Char(string='Duration', track_visibility='onchange')
    line_id = fields.Many2one('hr.manual.attendance.process', ondelete='cascade')
