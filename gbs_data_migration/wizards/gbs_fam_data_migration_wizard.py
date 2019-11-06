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
            datetime.datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            is_valid = False

        return is_valid

    @api.multi
    def get_existing_data(self):
        aac = {val.code: val.id for val in self.env['account.asset.category'].search([('active', '=', True)])}
        partner = {val.name: val.id for val in self.env['res.partner'].search([('supplier', '=', True), ('active', '=', True)])}
        branch = {val.code: val.id for val in self.env['operating.unit'].search([('active', '=', True)])}
        currency = {val.code: val.id for val in self.env['res.currency'].search([('active', '=', True)])}
        sou = {val.code: val.id for val in self.env['sub.operating.unit'].search([('active', '=', True)])}
        cc = {val.code: val.id for val in self.env['account.analytic.account'].search([('active', '=', True)])}
        jrnl = {val.code: val.id for val in self.env['account.journal'].search([('active', '=', True)])}

        return aac, partner, branch, currency, sou, cc, jrnl

    @api.multi
    def aml_import(self):
        if not self.lines:
            raise ValidationError(_('Please Select File.'))

        index = 0
        errors = ""
        self._err_log = ''
        move = self.env['gbs.data.migration'].browse(self._context['active_id'])
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)
        allow_header = ['asset code', 'asset name', 'asset type', 'type code', 'asset category', 'category code',
                        'batch no', 'vendor', 'invoice', 'model', 'bill date', 'warranty date', 'purchase date',
                        'usage date', 'last depr. date', 'purchase branch', 'current branch', 'sub operating unit',
                        'sou code', 'cost centre', 'currency', 'depr. base value', 'cost value', 'wdv', 'salvage value',
                        'accumulated depreciation', 'asset description', 'note', 'computation method',
                        'depreciation factor', 'asset life (in year)', 'depreciation history/date', 'depreciation history/days',
                        'depreciation history/depreciation', 'depreciation history/cumulative depreciation', 'depreciation history/wdv at date',
                        'allocation & transfer history/ from branch', 'allocation & transfer history/ to branch',
                        'allocation & transfer history/cost centre', 'allocation & transfer history/receive date']

        # retrieve existing data from database
        aac, partner, branch, currency, sou, cc, jrnl = self.get_existing_data()

        move_id = self.env['account.move'].create({
            'journal_id': jrnl['BILL'],
            'date': fields.Datetime.now(),
            'is_cbs': False,
            # 'ref': 'Opening Journal Entries',
            'line_ids': [],
            'amount': 0
        })

        journal_type = 'BILL'
        if journal_type not in jrnl.keys():
            raise Warning(_('[Wanring] Journal type [{0}]is not available.'.format(journal_type)))

        for line in reader:
            if set(line.keys()) != set(allow_header) or len(line.keys()) != len(allow_header):
                raise ValidationError(_(
                    "** Header of uploaed file does not match with expected one. \n Please check header of the file."))

            index += 1
            line_no = index + 1
            is_valid = True
            val = dict()

            # account.asset.asset
            asset_code = line['asset code'].strip()
            asset_name = line['asset name'].strip()
            asset_type = line['asset type'].strip()
            type_code = line['type code'].strip()
            asset_category = line['asset category'].strip()
            category_code = line['category code'].strip()
            batch_no = line['batch no'].strip()
            vendor = line['vendor'].strip()
            invoice = line['invoice'].strip()
            model_name = line['model'].strip()
            bill_date = line['bill date'].strip()
            warranty_date = line['warranty date'].strip()
            purchase_date = line['purchase date'].strip()
            usage_date = line['usage date'].strip()
            lst_depr_date = line['last depr. date'].strip()
            pb_code = line['purchase branch'].strip()
            cb_code = line['current branch'].strip()
            sou_name = line['sub operating unit'].strip()
            sou_code = line['sou code'].strip()
            cc_code = line['cost centre'].strip()
            currency_code = line['currency'].strip()
            # model = line['model'].strip()
            depr_base_value = float(line['depr. base value'].strip())
            cost_value = float(line['cost value'].strip())
            wdv = float(line['wdv'].strip())
            salvage_value = float(line['salvage value'].strip())
            accum_value = float(line['accumulated depreciation'].strip())
            asset_descr = line['asset description'].strip()
            note = line['note'].strip()
            comput_method = line['computation method'].strip()
            depr_factor = float(line['depreciation factor'].strip())
            depr_year = line['asset life (in year)'].strip()

            # account.asset.depreciation.line
            dh_date = line['depreciation history/date'].strip()
            dh_days = line['depreciation history/days'].strip()
            dh_depr_value = line['depreciation history/depreciation'].strip()
            dh_cum_depr = line['depreciation history/cumulative depreciation'].strip()
            dh_wdv_at_date_val = line['depreciation history/wdv at date'].strip()

            # account.asset.allocation.history
            ath_from_branch_code = line['allocation & transfer history/ from branch'].strip()
            ath_to_branch_code = line['allocation & transfer history/ to branch'].strip()
            ath_cc_code = line['allocation & transfer history/cost centre'].strip()
            ath_rcv_date = line['allocation & transfer history/receive date'].strip()

            if not asset_code:
                is_valid = False
                errors += self.format_error(line_no, 'Asset Code [{0}] invalid value'.format(asset_code))
            if not asset_name:
                is_valid = False
                errors += self.format_error(line_no, 'Asset Name [{0}] invalid value'.format(asset_name))
            if not asset_type:
                is_valid = False
                errors += self.format_error(line_no, 'Asset Type [{0}] invalid value'.format(asset_type))
            if type_code not in aac.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Asset Type Code [{0}] invalid value'.format(type_code))
            if not asset_category:
                is_valid = False
                errors += self.format_error(line_no, 'Asset Category [{0}] invalid value'.format(asset_category))
            if category_code not in aac.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Asset Category Code [{0}] invalid value'.format(category_code))
            if not batch_no:
                is_valid = False
                errors += self.format_error(line_no, 'Batch No [{0}] invalid value'.format(batch_no))
            if vendor not in partner.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Vendor [{0}] invalid value'.format(vendor))
            if not invoice:
                is_valid = False
                errors += self.format_error(line_no, 'Invoice [{0}] invalid value'.format(invoice))
            if not model_name:
                is_valid = False
                errors += self.format_error(line_no, 'Model [{0}] invalid value'.format(model_name))
            if not self.date_validate(bill_date):
                is_valid = False
                errors += self.format_error(line_no, 'Bill Date [{0}] invalid value'.format(bill_date))
            if not self.date_validate(warranty_date):
                is_valid = False
                errors += self.format_error(line_no, 'Warranty Date [{0}] invalid value'.format(warranty_date))
            if not self.date_validate(purchase_date):
                is_valid = False
                errors += self.format_error(line_no, 'Purchase Date [{0}] invalid value'.format(purchase_date))
            if not self.date_validate(usage_date):
                is_valid = False
                errors += self.format_error(line_no, 'Usage Date [{0}] invalid value'.format(usage_date))
            if not self.date_validate(lst_depr_date):
                is_valid = False
                errors += self.format_error(line_no, 'Last Depr. Date [{0}] invalid value'.format(lst_depr_date))
            if pb_code not in branch.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Purchase Branch Code [{0}] invalid value'.format(pb_code))
            if cb_code not in branch.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Current Branch Code [{0}] invalid value'.format(cb_code))
            if not sou_name:
                is_valid = False
                errors += self.format_error(line_no, 'Sub Operating Unit Name [{0}] invalid value'.format(sou_name))
            if sou_code not in sou.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Sub Operating Unit Code [{0}] invalid value'.format(sou_code))
            if cc_code not in cc.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Cost Center Code [{0}] invalid value'.format(cc_code))
            if currency_code not in currency.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Currency Code [{0}] invalid value'.format(currency_code))
            if not comput_method:
                is_valid = False
                errors += self.format_error(line_no, 'Computation Method [{0}] invalid value'.format(comput_method))
            if not depr_year:
                is_valid = False
                errors += self.format_error(line_no, 'Asset Life [{0}] invalid value'.format(depr_year))

            if not self.date_validate(dh_date):
                is_valid = False
                errors += self.format_error(line_no, 'Depreciation History Date [{0}] invalid value'.format(dh_date))

            if ath_from_branch_code not in branch.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Form Branch Code [{0}] invalid value'.format(ath_from_branch_code))
            if ath_to_branch_code not in branch.keys():
                is_valid = False
                errors += self.format_error(line_no, 'To Branch Code [{0}] invalid value'.format(cb_code))
            if ath_cc_code not in cc.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Cost Center Code [{0}] invalid value'.format(ath_cc_code))
            if not self.date_validate(ath_rcv_date):
                is_valid = False
                errors += self.format_error(line_no, 'Receive Date [{0}] invalid value'.format(ath_rcv_date))

            if is_valid:
                # make obj for account.asset.asset, account.asset.depreciation.line, account.asset.allocation.history
                # model
                pass


        # if len(errors) == 0:
        #     query = """
        #     INSERT INTO account_move_line
        #     (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
        #     analytic_account_id,segment_id,acquiring_channel_id,servicing_channel_id,credit,debit,amount_currency,company_id)
        #     VALUES %s""" % journal_entry[:-1]
        #     self.env.cr.execute(query)
        # else:
        #     file_path = os.path.join('/home/sumon/', 'errors.txt')
        #     with open(file_path, "w+") as file:
        #         file.write(errors)
