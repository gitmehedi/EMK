try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import base64
import csv

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError, Warning


class GBSFileImportWizard(models.TransientModel):
    _name = 'gbs.file.import.wizard'

    aml_data = fields.Binary(string='File')
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

    @api.multi
    def aml_import(self):
        if not self.lines:
            raise ValidationError(_('Please Select File.'))

        self._err_log = ''
        move = self.env['gbs.file.import'].browse(self._context['active_id'])
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)
        vals = []
        count = 0
        for line in reader:
            count += 1
            line_no = count + 1
            val = {}
            val['import_id'] = move.id
            val['account_no'] = line['account'].strip()
            if not val['account_no'] and not val['account_no'].isdigit():
                raise ValidationError(
                    _("Please check the file with values {0} and line no {1} !".format(val['account_no'], line_no)))

            val['narration'] = line['narration'].strip()
            if not val['narration']:
                raise ValidationError(
                    _("Please check the file with values {0} and line no {1} !".format(val['narration'], line_no)))

            val['reference_no'] = line['reference'].strip()
            val['date'] = line['date'].strip()
            if not val['date']:
                raise ValidationError(
                    _("Please check the file with values {0} and line no {1} !".format(val['date'], line_no)))

            val['type'] = line['type'].strip().lower()
            if not val['type']:
                raise ValidationError(
                    _("Please check the file with values {0} and line no {1} !".format(val['type'], line_no)))

            amount = line['amount'].strip()
            if not amount and not amount.isdigit():
                raise ValidationError(
                    _("Please check the file with values {0} and line no {1} !".format(amount, line_no)))

            if val['type'] == 'cr':
                val['credit'] = amount
                val['debit'] = 0
            if val['type'] == 'dr':
                val['credit'] = 0
                val['debit'] = amount
            vals.append((0, 0, val))

        res = move.write({'import_lines': vals})
        import_line = len(move.import_lines)
        if import_line is not count and not res:
            msg = "Summary of Importing:\n - Total lines of import files is {0} \n - Valid record is {1} \n Please check the import file".format(
                count, import_line)
            raise ValidationError(_(msg))
        else:
            return True
