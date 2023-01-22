try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import base64, os
import csv, datetime, time

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError, Warning


class GBSCOAImportWizard(models.TransientModel):
    _name = 'gbs.coa.data.migration.wizard'

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

    @api.multi
    def get_existing_data(self):
        self.env.cr.execute('SELECT code,id FROM account_account')
        coa = {val[0]: val[1] for val in self.env.cr.fetchall()}
        aat = {val.name: val.id for val in self.env['account.account.type'].search([('active', '=', True)])}
        ly = {val.name: val.id for val in self.env['account.account.level'].search([])}
        return coa, aat, ly

    @api.multi
    def aml_import(self):
        start = time.time()
        if not self.lines:
            raise ValidationError(_('Please Select File.'))

        index = 0
        errors = ""

        self._err_log = ''
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)
        allow_header = ['layer',
                        'code',
                        'name',
                        'parent account',
                        'type',
                        'active',
                        'pending',
                        'status',
                        'allow reconciliation']

        # retrieve existing data from database
        coa, aat, ly = self.get_existing_data()

        for line in reader:
            if 'allow reconciliation' not in line.keys():
                line['allow reconciliation'] = ''

            if set(line.keys()) != set(allow_header) or len(line.keys()) != len(allow_header):
                raise ValidationError(_(
                    "** Header of uploaed file does not match with expected one. \n Please check header of the file."))

            index += 1
            line_no = index + 1
            val = {}

            layer = line['layer'].strip()
            code = line['code'].strip()
            name = line['name'].strip()
            parent = line['parent account'].strip()
            type = line['type'].strip()
            reconciliation = line['allow reconciliation'].strip()
            pending = line['pending'].strip()
            status = line['status'].strip()
            active = line['active'].strip()

            if layer not in ly.keys():
                errors += self.format_error(line_no, 'Layer [{0}] invalid value'.format(layer))

            if code in coa.keys():
                continue

            if type not in aat.keys():
                type_obj = self.env['account.account.type'].create({'name': type, 'type': 'other'})
                aat[type] = type_obj.id

            if parent not in coa.keys():
                errors += self.format_error(line_no, 'Parent Code [{0}] invalid value'.format(parent))

            if len(errors) == 0:
                val['level_id'] = ly[layer]
                val['code'] = code
                val['name'] = name
                val['parent_id'] = coa[parent]
                val['allow_reconcilation'] = reconciliation
                val['active'] = active
                val['pending'] = pending
                val['status'] = status
                val['user_type_id'] = aat[type]
                self.env['account.account'].create(val)
                print(line_no)

        end = time.time()
        print('Total Execution Time: {0}'.format(end - start))

        if len(errors) > 0:
            file_path = os.path.join(os.path.expanduser("~"), "COA_ERR_" + fields.Datetime.now())
            with open(file_path, "w+") as file:
                file.write(errors)
