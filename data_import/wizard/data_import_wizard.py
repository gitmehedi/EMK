try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import base64, datetime, csv
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning

_logger = logging.getLogger(__name__)


class DataImportWizard(models.TransientModel):
    _name = 'data.import.wizard'

    aml_data = fields.Binary(string='File')
    aml_fname = fields.Char(string='Filename')
    lines = fields.Binary(compute='_compute_lines', string='Input Lines')
    dialect = fields.Binary(compute='_compute_dialect', string='Dialect')
    csv_separator = fields.Selection([(',', ', (comma)'), (';', '; (semicolon)')],
                                     string='CSV Separator', default=',', required=True)
    decimal_separator = fields.Selection([('.', '. (dot)'), (',', ', (comma)')],
                                         string='Decimal Separator', default='.')
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
        if not lines:
            raise Warning(_('Please Select Data File to Import.'))

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

        self._field_methods = {}
        self._skip_fields = []

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
                header_fields2.append(hf)

        for i, hf in enumerate(header_fields):

            if hf in self._field_methods:
                continue

        return header_fields

    @api.multi
    def aml_import(self):
        self._err_log = ''
        event = self.env[self._context['active_model']].browse(self._context['active_id'])
        self._sum_debit = self._sum_credit = 0.0
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(
            StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)

        obj = self.env['event.registration']
        partner = self.env['res.partner'].search([('name', '=', 'Public user'), ('active', '=', False)])
        for line in reader:
            vals = {}
            vals['name'] = line['name'] if 'name' in line else None
            vals['email'] = line['email'] if 'email' in line else None
            vals['phone'] = line['phone'] if 'phone' in line else None
            vals['date_open'] = line['date_open'] if 'date_open' in line else None
            vals['date_closed'] = line['date_closed'] if 'date_closed' in line else None
            vals['partner_id'] = partner.id if partner else None
            vals['event_id'] = event.id
            obj.create(vals)


def str2float(amount, decimal_separator):
    if not amount:
        return 0.0
    try:
        if decimal_separator == '.':
            return float(amount.replace(',', ''))
        else:
            return float(amount.replace('.', '').replace(',', '.'))
    except:
        return False


def str2int(amount, decimal_separator):
    if not amount:
        return 0
    try:
        if decimal_separator == '.':
            return int(amount.replace(',', ''))
        else:
            return int(amount.replace('.', '').replace(',', '.'))
    except:
        return False
