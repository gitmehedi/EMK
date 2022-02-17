try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import base64
import csv
import datetime
import logging
import os

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError, Warning


class HrManualAttendanceProcess(models.TransientModel):
    _name = 'hr.manual.attendance.process.wizard'

    aml_data = fields.Binary(string='Attendance (CSV) File')
    aml_fname = fields.Char(string='Filename')
    lines = fields.Binary(compute='_compute_lines', string='Input Lines')
    dialect = fields.Binary(compute='_compute_dialect', string='Dialect')
    csv_separator = fields.Selection([(',', ', (comma)'), (';', '; (semicolon)')], default=',', string='CSV Separator',
                                     required=True)
    decimal_separator = fields.Selection([('.', '. (dot)'), (',', ', (comma)')], string='Decimal Separator',
                                         default='.')
    codepage = fields.Char(string='Code Page', default=lambda self: self._default_codepage(),
                           help="Code Page of the system that has generated the csv file."
                                "\nE.g. Windows-1252, utf-8")
    note = fields.Text('Log')
    date = fields.Date(string='Attendance Date', default=fields.Datetime.now, required=True)

    @api.model
    def _default_codepage(self):
        return 'Windows-1252'

    @api.one
    @api.depends('aml_data')
    def _compute_lines(self):
        if self.aml_data:
            lines = base64.decodestring(self.aml_data)
            # convert windows & mac line endings to unix style
            self.lines = lines.replace('\r\n', '\n').replace('\r', '\n')

    @api.one
    @api.depends('lines', 'csv_separator')
    def _compute_dialect(self):
        if self.lines:
            try:
                self.dialect = csv.Sniffer().sniff(
                    self.lines[:128], delimiters=';,')
            except:
                # csv.Sniffer is not always reliable
                # in the detection of the delimiter
                self.dialect = csv.Sniffer().sniff(
                    '"header 1";"header 2";\r\n')
                if ',' in self.lines[128]:
                    self.dialect.delimiter = ','
                elif ';' in self.lines[128]:
                    self.dialect.delimiter = ';'
        if self.csv_separator:
            self.dialect.delimiter = str(self.csv_separator)

    @api.onchange('aml_data')
    def _onchange_aml_data(self):
        if self.lines:
            self.csv_separator = self.dialect.delimiter
            if self.csv_separator == ';':
                self.decimal_separator = ','

    @api.onchange('csv_separator')
    def _onchange_csv_separator(self):
        if self.csv_separator and self.aml_data:
            self.dialect.delimiter = self.csv_separator

    def _remove_leading_lines(self, lines):
        """ remove leading blank or comment lines """
        input = StringIO.StringIO(lines)
        header = False
        while not header:
            ln = input.next()
            if not ln or ln and ln[0] in [self.csv_separator, '#']:
                continue
            else:
                header = ln.lower()
        if not header:
            raise Warning(
                _("No header line found in the input file !"))
        output = input.read()
        return output, header

    def _process_header(self, header_fields):
        # header fields after blank column are considered as comments
        column_cnt = 0
        for cnt in range(len(header_fields)):
            if header_fields[cnt] == '':
                column_cnt = cnt
                break
            elif cnt == len(header_fields) - 1:
                column_cnt = cnt + 1
                break
        header_fields = header_fields[:column_cnt]

        # check for duplicate header fields
        header_fields2 = []
        for hf in header_fields:
            if hf in header_fields2:
                raise Warning(_(
                    "Duplicate header field '%s' found !"
                    "\nPlease correct the input file.")
                              % hf)
            else:
                header_fields2.append(hf.strip())

        return header_fields2

    def _log_line_error(self, line, msg):
        data = self.csv_separator.join(
            [line[hf] for hf in self._header_fields])
        self._err_log += _(
            "Error when processing line '%s'") % data + ':\n' + msg + '\n\n'

    @staticmethod
    def format_error(index, text):
        return "({0},'{1}','{2}'),".format(index, text, fields.Datetime.now())

    @staticmethod
    def date_validate(date_str):
        is_valid = True
        try:
            datetime.datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            is_valid = False

        return is_valid

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

    @staticmethod
    def date_validate(date_str):
        is_valid = True
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            is_valid = False

        return is_valid

    @api.multi
    def get_existing_data(self):
        terminal = {val.code: val.id for val in
                    self.env['hr.attendance.terminal'].search([('active', '=', True), ('is_attendance', '=', True)])}
        employee = {val.employee_number: val.id for val in self.env['hr.employee'].search([('active', '=', True)])}
        card = {val.code: val.id for val in self.env['hr.attendance.card'].search([('active', '=', True)])}

        return terminal, employee, card

    @api.multi
    def process_manual_attendance(self):
        if not self.lines:
            raise ValidationError(_('Please Select File.'))

        context = self._context
        index = 0

        self._err_log = ''
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)
        terminal, employee, card = self.get_existing_data()

        errors, record_entry = "", ""

        for line in reader:
            # if set(line.keys()) != set(allow_header) or len(line.keys()) != len(allow_header):
            #     raise ValidationError(_(
            #         "** Header of uploaed file does not match with expected one. \n Please check header of the file."))

            process = self.env[context['active_model']].browse(context['active_id'])
            index += 1
            line_no = index + 1
            is_valid = True
            val = dict()

            date_str = line['date'].strip()
            time = line['time'].strip()
            terminal_split = line['terminal id'].split(':')
            terminal_id = terminal_split[0].strip() if len(terminal_split) > 0 else ''
            employee_id = line['user id'].strip()
            mode = line['mode'].strip()
            card_id = line['card serial no.'].strip()
            result = line['result'].strip()
            type = line['type'].strip()

            # if employee_id not in employee.keys():
            #     if len(employee_id) < 7:
            #         is_valid = False
            #         errors += self.format_error(line_no, 'Employee [{0}] invalid value'.format(employee_id))

            if (terminal_id in terminal.keys()) and (employee_id in employee.keys()):
                val['date'] = date_str
                val['time'] = time
                val['terminal_id'] = terminal[terminal_id] if terminal_id else 'null'
                val['card_serial_id'] = 'null'
                val['employee_id'] = employee[employee_id] if employee_id else 'null'
                val['result'] = result
                val['mode'] = mode
                val['type'] = type
                val['line_id'] = context['active_id']

                record_entry += self.format_record(val)

        if len(errors) == 0:
            query = """
            INSERT INTO hr_manual_attendance_process_line 
            (date, time,result, mode, type, card_serial_id,terminal_id, employee_id, line_id)  
            VALUES %s""" % record_entry[:-1]
            self.env.cr.execute(query)

            process.write({
                'attendance_filename': self.aml_fname,
                'attendance_file': self.aml_data})

        else:
            file_path = os.path.join(os.path.expanduser("~"), "GL_ERR_" + fields.Datetime.now())
            with open(file_path, "w+") as file:
                file.write(errors)

            # process.write({
            #     'attendance_filename': self.aml_fname,
            #     'attendance_file': self.aml_data,
            #     'error_file': base64.b64encode(self.file),
            #     'error_filename': self.aml_fname,
            # })
