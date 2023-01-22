try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import base64, os
import csv, datetime
import numpy as np

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError, Warning


class GBSFileImportWizard(models.TransientModel):
    _name = 'gbs.data.migration.wizard'

    aml_data = fields.Binary(string='File')
    aml_fname = fields.Char(string='Filename')
    lines = fields.Binary(compute='_compute_lines', string='Input Lines')
    dialect = fields.Binary(compute='_compute_dialect', string='Dialect')
    csv_separator = fields.Selection([('|', ', (comma)'), (';', '; (semicolon)')], default='|', string='CSV Separator',
                                     required=True)
    decimal_separator = fields.Selection([('.', '. (dot)'), (',', ', (comma)')], string='Decimal Separator',
                                         default='.')
    codepage = fields.Char(string='Code Page', default=lambda self: self._default_codepage(),
                           help="Code Page of the system that has generated the csv file."
                                "\nE.g. Windows-1252, utf-8")
    note = fields.Text('Log')
    date = fields.Date(string='Generate Date', required=True)
    dollar_rate = fields.Float(string='Dollar Rate', required=True)

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
                if '|' in self.lines[128]:
                    self.dialect.delimiter = '|'
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
    def format_journal(line):
        return "({0},'{1}','{2}',{3},{4},'{5}','{6}',{7},{8},{9},{10},{11},{12},{13},{14},{15},{16}),".format(
            line['move_id'],
            line['date'],
            line['date_maturity'],
            line['operating_unit_id'],
            line['account_id'],
            line['name'],
            line['name'],
            line['currency_id'],
            line['journal_id'],
            line['analytic_account_id'],
            line['segment_id'],
            line['acquiring_channel_id'],
            line['servicing_channel_id'],
            line['credit'],
            line['debit'],
            line['amount_currency'],
            line['company_id'])

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
        coa = {val.code: val.id for val in
               self.env['account.account'].search([('level_id.name', '=', 'Layer 5'), ('active', '=', True)])}
        jrnl = {val.code: val.id for val in self.env['account.journal'].search([('active', '=', True)])}
        branch = {val.code: val.id for val in self.env['operating.unit'].search([('active', '=', True)])}
        currency = {val.code: val.id for val in self.env['res.currency'].search([('active', '=', True)])}
        ac = {val.code: val.id for val in self.env['acquiring.channel'].search([('active', '=', True)])}
        sc = {val.code: val.id for val in self.env['servicing.channel'].search([('active', '=', True)])}
        sg = {val.code: val.id for val in self.env['segment'].search([('active', '=', True)])}
        cc = {val.code: val.id for val in
              self.env['account.analytic.account'].search([('active', '=', True)])}

        return coa, jrnl, branch, currency, ac, sc, sg, cc

    @api.multi
    def aml_import(self):
        if not self.lines:
            raise ValidationError(_('Please Select File.'))

        index = 0
        self._err_log = ''
        move = self.env['gbs.data.migration'].browse(self._context['active_id'])
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)
        allow_header = ['dt', 'brnch', 'segment code', 'gl code', 'acquiring channel code', 'servicing channel code',
                        'cost center code', 'narration', 'cr amt', 'dr amt', 'lcy bal']

        coa, jrnl, branch, currency, ac, sc, sg, cc = self.get_existing_data()
        move_id = self.env['account.move'].create({
            'journal_id': jrnl['CBS'],
            'date': self.date,
            'is_cbs': True,
            'ref': 'Opening Journal Entries',
            'line_ids': [],
            'amount': 0
        })

        journal_type = 'CBS'
        if journal_type not in jrnl.keys():
            raise Warning(_('[Wanring] Journal type [{0}]is not available.'.format(journal_type)))

        errors, journal_entry = "", ""

        for line in reader:
            if set(line.keys()) != set(allow_header) or len(line.keys()) != len(allow_header):
                raise ValidationError(_(
                    "** Header of uploaed file does not match with expected one. \n Please check header of the file."))

            index += 1
            line_no = index + 1
            is_valid = True
            val = dict()

            credit_amt = abs(np.float128(line['cr amt'].strip()))
            debit_amt = abs(np.float128(line['dr amt'].strip()))
            lcy_amt = np.float128(line['lcy bal'].strip())


            if credit_amt or debit_amt or lcy_amt:
                date_str = line['dt'].strip()
                branch_code = line['brnch'].strip()[-3:]
                sg_code = line['segment code'].strip()
                gl_code = line['gl code'].strip()
                ac_code = line['acquiring channel code'].strip()
                sc_code = line['servicing channel code'].strip()
                cc_code = line['cost center code'].strip()
                narration = line['narration'].strip()
                cur_code = line['narration'].strip()[3:6]

                if gl_code not in coa.keys():
                    is_valid = False
                    errors += self.format_error(line_no, 'Account [{0}] invalid value'.format(gl_code))
                if branch_code not in branch.keys():
                    is_valid = False
                    errors += self.format_error(line_no, 'Branch [{0}] invalid value'.format(branch_code))
                if cur_code not in currency.keys():
                    is_valid = False
                    errors += self.format_error(line_no, 'Currency [{0}] invalid value'.format(cur_code))
                if sg_code not in sg.keys() and sg_code != '0':
                    is_valid = False
                    errors += self.format_error(line_no, 'Segment [{0}] invalid value'.format(sg_code))
                if ac_code not in ac.keys() and ac_code != '00':
                    is_valid = False
                    errors += self.format_error(line_no, 'Acquiring Channel [{0}] invalid value'.format(ac_code))
                if sc_code not in sc.keys() and sc_code != '00':
                    is_valid = False
                    errors += self.format_error(line_no, 'Servicing Channel [{0}] invalid value'.format(sc_code))
                if cc_code not in cc.keys() and cc_code != '000':
                    is_valid = False
                    errors += self.format_error(line_no, 'Cost Center [{0}] invalid value'.format(cc_code))
                if not narration:
                    is_valid = False
                    errors += self.format_error(line_no, 'Narration [{0}] invalid value'.format(narration))
                if not self.date_validate(date_str):
                    is_valid = False
                    errors += self.format_error(line_no, 'Date [{0}] invalid value'.format(date_str))

                if is_valid:
                    val['move_id'] = move_id.id
                    val['name'] = narration
                    val['account_id'] = coa[gl_code]
                    val['journal_id'] = jrnl['CBS']
                    val['analytic_account_id'] = cc[cc_code] if cc_code != '000' else 'NULL'
                    val['currency_id'] = currency[cur_code]
                    val['segment_id'] = sg[sg_code] if sg_code != '0' else 'NULL'
                    val['acquiring_channel_id'] = ac[ac_code] if ac_code != '00' else 'NULL'
                    val['servicing_channel_id'] = sc[sc_code] if sc_code != '00' else 'NULL'
                    val['operating_unit_id'] = branch[branch_code]
                    val['date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%m-%d-%y')
                    val['date_maturity'] = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%m-%d-%y')
                    val['company_id'] = self.env.user.company_id.id

                    # For BDT Only
                    if cur_code == 'BDT':
                        val['debit'] = "{:.3f}".format(debit_amt)
                        val['credit'] = "{:.3f}".format(credit_amt)
                        val['amount_currency'] = 0
                    # For OBU Only
                    elif branch_code == '116' and cur_code == 'USD':
                        val['debit'] = "{:.3f}".format(abs(debit_amt) * self.dollar_rate)
                        val['credit'] = "{:.3f}".format(abs(credit_amt) * self.dollar_rate)

                        if credit_amt > 0:
                            val['amount_currency'] = "{:.3f}".format(credit_amt)
                        else:
                            val['amount_currency'] = "-{:.3f}".format(debit_amt)
                    else:
                        if lcy_amt > 0:
                            val['credit'] = "{:.3f}".format(abs(lcy_amt))
                            val['debit'] = 0
                        else:
                            val['credit'] = 0
                            val['debit'] = "{:.3f}".format(abs(lcy_amt))

                        if credit_amt > 0:
                            val['amount_currency'] = "{:.3f}".format(credit_amt)
                        else:
                            val['amount_currency'] = "-{:.3f}".format(debit_amt)

                    journal_entry += self.format_journal(val)

        if len(errors) == 0:
            query = """
            INSERT INTO account_move_line 
            (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
            analytic_account_id,segment_id,acquiring_channel_id,servicing_channel_id,credit,debit,amount_currency,company_id)  
            VALUES %s""" % journal_entry[:-1]
            self.env.cr.execute(query)
        else:
            file_path = os.path.join(os.path.expanduser("~"), "GL_ERR_" + fields.Datetime.now())
            with open(file_path, "w+") as file:
                file.write(errors)


class ServerFileError(models.Model):
    _name = 'gbs.migration.error'
    _description = "File Processing Error"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'

    name = fields.Char(string='Name')
    line_ids = fields.One2many('server.file.error.line', 'line_id', readonly=True)


class ServerFileErrorDetails(models.Model):
    _name = 'gbs.migration.error.line'
    _description = "File Processing Error Details"
    _inherit = ["mail.thread"]
    _order = 'id asc'

    process_date = fields.Datetime(default=fields.Datetime.now)
    line_no = fields.Char(string='Line No')
    status = fields.Boolean(default=False, string='Status')
    details = fields.Text(string='Error Details')
    line_id = fields.Many2one('gbs.migration.error', ondelete='cascade')
