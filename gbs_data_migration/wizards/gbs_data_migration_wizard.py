try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import base64, os
import csv, datetime

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

    def format_error(self, id, index, text):
        return "({0},{1},'{2}','{3}'),".format(id, index, text, fields.Datetime.now())

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

    @api.multi
    def aml_import(self):
        if not self.lines:
            raise ValidationError(_('Please Select File.'))

        self._err_log = ''
        move = self.env['gbs.data.migration'].browse(self._context['active_id'])
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)
        index = 0
        allow_header = ['dt', 'brnch', 'segment code', 'gl code', 'acquiring channel code', 'servicing channel code',
                        'cost center code', 'narration', 'cr amt', 'dr amt', 'lcy bal']

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

        errObj = self.env['gbs.migration.error'].create({'name': 'Opening Journal'})
        move_id = self.env['account.move'].create({
            'journal_id': jrnl['CBS'],
            'date': fields.Datetime.now(),
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
            val = {}
            credit_amt = abs(float(line['cr amt'].strip()))
            debit_amt = abs(float(line['dr amt'].strip()))
            lcy_amt = abs(float(line['lcy bal'].strip()))
            if credit_amt or debit_amt or lcy_amt:

                # date = self.date_validate(line['dt'].strip())
                branch_code = line['brnch'].strip()[-3:]
                sg_code = line['segment code'].strip()
                gl_code = line['gl code'].strip()
                ac_code = line['acquiring channel code'].strip()
                sc_code = line['servicing channel code'].strip()
                cc_code = line['cost center code'].strip()
                narration = line['narration'].strip()
                cur_code = line['narration'].strip()[3:6]

                if gl_code in coa.keys():
                    val['account_id'] = coa[gl_code]
                else:
                    errors += self.format_error(errObj.id, line_no, 'Account [{0}] invalid value'.format(gl_code))

                if branch_code in branch.keys():
                    val['branch_id'] = branch[branch_code]
                else:
                    errors += self.format_error(errObj.id, line_no, 'Branch [{0}] invalid value'.format(branch_code))

                if sg_code in sg.keys():
                    val['segment_id'] = sg[sg_code]
                else:
                    if sg_code == '0':
                        sg['0'] = 'NULL'
                    else:
                        errors += self.format_error(errObj.id, line_no, 'Segment [{0}] invalid value'.format(sg_code))

                if ac_code in ac.keys():
                    val['acquiring_channel_id'] = ac[ac_code]
                else:
                    if ac_code == '00':
                        ac['00'] = 'NULL'
                    else:
                        errors += self.format_error(errObj.id, line_no,
                                                    'Acquiring Channel [{0}] invalid value'.format(ac_code))

                if sc_code in sc.keys():
                    val['servicing_channel_id'] = sc[sc_code]
                else:
                    if sc_code == '00':
                        sc['00'] = 'NULL'
                    else:
                        errors += self.format_error(errObj.id, line_no,
                                                    'Servicing Channel [{0}] invalid value'.format(sc_code))

                if cc_code in cc.keys():
                    val['analytic_account_id'] = cc[cc_code]
                else:
                    if cc_code == '000':
                        cc['000'] = 'NULL'
                    else:
                        errors += self.format_error(errObj.id, line_no,
                                                    'Cost Center [{0}] invalid value'.format(cc_code))

                if narration:
                    val['narration'] = narration
                else:
                    errors += self.format_error(errObj.id, line_no, 'Narration [{0}] invalid value'.format(narration))

                if cur_code in currency.keys():
                    val['currency'] = currency[cur_code]
                else:
                    errors += self.format_error(errObj.id, line_no, 'Currency [{0}] invalid value'.format(cur_code))

                dt = line['dt'].split('-')
                date = '{0}-{1}-{2}'.format(dt[1], dt[2], dt[0])
                # if date:
                #     val['date'] = '2019-02-02'
                # else:
                #     errors += self.format_error(line_no, 'Date [{0}] invalid value'.format(line['dt']))

                if len(errors) == 0:
                    val = {
                        'move_id': move_id.id,
                        'name': narration,
                        'account_id': coa[gl_code],
                        'journal_id': jrnl['CBS'],
                        'analytic_account_id': cc[cc_code],
                        'currency_id': currency[cur_code],
                        'segment_id': sg[sg_code],
                        'acquiring_channel_id': ac[ac_code],
                        'servicing_channel_id': sc[sc_code],
                        'operating_unit_id': branch[branch_code],
                        'date': date,
                        'date_maturity': date,
                        'company_id': self.env.user.company_id.id,
                    }

                    # For BDT Only
                    if cur_code == 'BDT':
                        val['debit'] = abs(debit_amt)
                        val['credit'] = abs(credit_amt)
                        val['amount_currency'] = 0
                    # For OBU Only
                    elif branch_code == 116 and cur_code == 'USD':
                        val['debit'] = abs(debit_amt) * 84.75
                        val['credit'] = abs(credit_amt) * 84.75

                        if credit_amt > 0:
                            val['amount_currency'] = credit_amt
                        else:
                            val['amount_currency'] = debit_amt
                    else:
                        if lcy_amt > 0:
                            val['credit'] = abs(lcy_amt)
                            val['debit'] = 0
                        else:
                            val['credit'] = 0
                            val['debit'] = abs(lcy_amt)

                        if credit_amt > 0:
                            val['amount_currency'] = credit_amt
                        else:
                            val['amount_currency'] = debit_amt

                    journal_entry += self.format_journal(val)

        if len(errors) == 0:
            query = """
            INSERT INTO account_move_line 
            (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
            analytic_account_id,segment_id,acquiring_channel_id,servicing_channel_id,credit,debit,amount_currency,company_id)  
            VALUES %s""" % journal_entry[:-1]
            self.env.cr.execute(query)

            # if move_id.state == 'draft':
            #     move_id.sudo().post()
            #     return move_id
        else:
            file_path = os.path.join('/home/sumon/', 'errors.txt')

            with open(file_path, "w+") as file:
                file.write(errors)

    def date_validate(self, data):
        if '-' in data:
            date = data.split('-')
        else:
            date = data.split('/')

        if len(date) != 3:
            return False

        is_valid = True
        try:
            datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
        except ValueError:
            is_valid = False

        return is_valid


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
