import os, shutil, base64, csv

from odoo import api, models, fields, _
from odoo.addons.hr_attendance_store.helpers import helper
from odoo.exceptions import ValidationError


class HrManualAttendanceProcess(models.Model):
    _name = 'hr.manual.attendance.process'
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _description = "Import File"
    _rec_name = 'date'
    _order = 'id desc'

    name = fields.Char(string='Serial No', track_visibility='onchange')
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
            name = self.env['ir.sequence'].sudo().next_by_code('asset.depreciation.change.request')
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
            self.write({
                'name':name,
                'state':'filter',
            })

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
            self.state = 'approve'

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

    @api.model
    def _import_hr_manual_attendance(self):
        """Run all scheduled backups."""
        integration = self.env['middleware.configuration'].search([('type', '=', 'interface'),
                                                                   ('method', '=', 'sftp'),
                                                                   ('status', '=', True)], limit=1)
        if not integration:
            raise ValidationError(_("Record is not available with proper configuration"))
        return self.import_attendance_date(integration)

    @api.multi
    def get_existing_data(self):
        terminal = {val.code: val.id for val in
                    self.env['hr.attendance.terminal'].search([('active', '=', True), ('is_attendance', '=', True)])}
        employee = {val.employee_number: val.id for val in self.env['hr.employee'].search([('active', '=', True)])}
        card = {val.code: val.id for val in self.env['hr.attendance.card'].search([('active', '=', True)])}

        return terminal, employee, card

    @staticmethod
    def format_record(line):
        return "('{0}','{1}','{2}','{3}','{4}',{5},{6},{7},{8}),".format(
            line['date'],
            line['time'],
            line['result'],
            line['mode'],
            line['type'],
            line['card_serial_id'],
            line['terminal_id'],
            line['employee_id'],
            line['line_id'])

    @api.multi
    def import_attendance_date(self, integration):
        files = integration.get_source_files(integration, extension='.csv')
        for fl in files:
            local_path = os.path.join(integration.folder, fl)
            terminal, employee, card = self.get_existing_data()
            errors, record_entry = "", ""

            with open(local_path, 'r') as file_ins:
                index = 0
                readline = csv.DictReader(file_ins)
                data = open(local_path, 'rb').read()
                base64_encoded = base64.b64encode(data).decode('UTF-8')
                process = self.create({'date': fields.Datetime.now(),
                                       'attendance_filename': fl,
                                       'attendance_file': base64_encoded,
                                       })

                for line in readline:
                    index += 1
                    line = line
                    if len(line) > 2:
                        val = dict()
                        date_str = line['Date'].strip()
                        time = line['Time'].strip()
                        terminal_split = line['Terminal ID'].split(':')
                        terminal_id = terminal_split[0].strip() if len(terminal_split) > 0 else ''
                        employee_id = line['User ID'].strip()
                        mode = line['Mode'].strip()
                        card_id = line['Card Serial No.'].strip()
                        result = line['Result'].strip()
                        type = line['Type'].strip()

                        if (terminal_id in terminal.keys()) and (employee_id in employee.keys()):
                            val['date'] = date_str
                            val['time'] = time
                            val['terminal_id'] = terminal[terminal_id] if terminal_id else 'null'
                            val['card_serial_id'] = 'null'
                            val['employee_id'] = employee[employee_id] if employee_id else 'null'
                            val['result'] = result
                            val['mode'] = mode
                            val['type'] = type
                            val['line_id'] = process.id

                            record_entry += self.format_record(val)

                if len(errors) == 0:
                    query = """
                        INSERT INTO hr_manual_attendance_process_line
                        (date, time,result, mode, type, card_serial_id,terminal_id, employee_id, line_id)
                        VALUES %s""" % record_entry[:-1]
                    self.env.cr.execute(query)

                    process.act_filter()
                    if process.state == 'filter':
                        process.act_approve()
                    integration._put_files_destination(fl)


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
