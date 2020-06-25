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


class GBSFileImportWizard(models.TransientModel):
    _name = 'gbs.fam.data.migration.wizard'

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
        aac = {val.code: val.id for val in self.env['account.asset.category'].search([('active', '=', True)])}
        partner = {val.name: val.id for val in
                   self.env['res.partner'].search([('supplier', '=', True), ('active', '=', True)])}
        branch = {val.code: val.id for val in self.env['operating.unit'].search([('active', '=', True)])}
        currency = {val.code: val.id for val in self.env['res.currency'].search([('active', '=', True)])}
        sou = {val.code: val.id for val in self.env['sub.operating.unit'].search([('active', '=', True)])}
        cc = {val.code: val.id for val in self.env['account.analytic.account'].search([('active', '=', True)])}
        jrnl = {val.code: val.id for val in self.env['account.journal'].search([('active', '=', True)])}

        return aac, partner, branch, currency, sou, cc, jrnl

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
        allow_header = ['asset code',
                        'asset name',
                        'asset type',
                        'asset category',
                        'batch no',
                        'vendor',
                        'invoice',
                        'model',
                        'bill date',
                        'warranty date',
                        'purchase date',
                        'usage date',
                        'last depr. date',
                        'purchase branch',
                        'current branch',
                        'sub operating unit',
                        'cost centre',
                        'currency',
                        'depr. base value',
                        'cost value',
                        'wdv',
                        'salvage value',
                        'accumulated depreciation',
                        'asset description',
                        'note',
                        'computation method',
                        'depreciation factor',
                        'asset life (in year)']

        # retrieve existing data from database
        aac, partner, branch, currency, sou, cc, jrnl = self.get_existing_data()
        # computation method
        cm = {'No Depreciation': 'no_depreciation', 'Reducing Method': 'degressive', 'Straight Line/Linear': 'linear'}

        for line in reader:
            if set(line.keys()) != set(allow_header) or len(line.keys()) != len(allow_header):
                if len(line.keys()) > len(allow_header):
                    header_mis = list(set(line.keys()) - set(allow_header))
                    raise ValidationError(_("Remove Header from file with name {0}.".format(header_mis)))
                else:
                    header_mis = list(set(allow_header) - set(line.keys()))
                    raise ValidationError(_("Add Header in file with name {0}.".format(header_mis)))

            index += 1
            line_no = index + 1
            val = {}

            asset_code = line['asset code'].strip()
            asset_name = line['asset name'].strip()
            asset_type = line['asset type'].strip()
            asset_category = line['asset category'].strip()
            vendor = line['vendor'].strip()
            model_name = line['model'].strip()
            warranty_date = line['warranty date'].strip()
            purchase_date = line['purchase date'].strip()
            usage_date = line['usage date'].strip()
            lst_depr_date = line['last depr. date'].strip()
            pb_code = line['purchase branch'].strip()
            cb_code = line['current branch'].strip()
            # sou_code = line['sub operating unit'].strip()
            sou_code = '001'
            cc_code = line['cost centre'].strip()
            currency_code = line['currency'].strip()
            depr_base_value = float(line['depr. base value'].strip().replace(',', ''))
            cost_value = float(line['cost value'].strip().replace(',', ''))
            wdv = float(line['wdv'].strip().replace(',', ''))
            salvage_value = float(line['salvage value'].strip().replace(',', ''))
            accum_value = float(line['accumulated depreciation'].strip().replace(',', ''))
            asset_descr = line['asset description'].strip()
            note = line['note'].strip()
            cm_code = line['computation method'].strip()
            depr_factor = line['depreciation factor'].strip()
            depr_year = line['asset life (in year)'].strip()

            if not asset_name:
                errors += self.format_error(line_no, 'Asset Name [{0}] invalid value'.format(asset_name))

            if asset_type not in aac.keys():
                errors += self.format_error(line_no, 'Asset Type Code [{0}] invalid value'.format(asset_type))

            if asset_category not in aac.keys():
                errors += self.format_error(line_no, 'Asset Category Code [{0}] invalid value'.format(asset_category))

            if not self.date_validate(warranty_date):
                errors += self.format_error(line_no, 'Warranty Date [{0}] invalid value'.format(warranty_date))

            if not self.date_validate(purchase_date):
                errors += self.format_error(line_no, 'Purchase Date [{0}] invalid value'.format(purchase_date))

            if not self.date_validate(usage_date):
                errors += self.format_error(line_no, 'Usage Date [{0}] invalid value'.format(usage_date))

            if not self.date_validate(lst_depr_date) and cm_code != 'No Depreciation':
                errors += self.format_error(line_no, 'Last Depr. Date [{0}] invalid value'.format(lst_depr_date))

            if pb_code not in branch.keys():
                errors += self.format_error(line_no, 'Purchase Branch Code [{0}] invalid value'.format(pb_code))

            if cb_code not in branch.keys():
                errors += self.format_error(line_no, 'Current Branch Code [{0}] invalid value'.format(cb_code))

            if sou_code not in sou.keys():
                errors += self.format_error(line_no, 'Sequence Code [{0}] invalid value'.format(sou_code))

            if cc_code not in cc.keys():
                errors += self.format_error(line_no, 'Cost Center Code [{0}] invalid value'.format(cc_code))

            if currency_code not in currency.keys():
                errors += self.format_error(line_no, 'Currency Code [{0}] invalid value'.format(currency_code))

            if cm_code not in cm.keys():
                errors += self.format_error(line_no, 'Computation Method [{0}] invalid value'.format(cm_code))

            if vendor == 'N/A' or not vendor:
                val['partner_id'] = False
            elif vendor in partner.keys():
                val['partner_id'] = partner[vendor]
            else:
                partner_id = self.env['res.partner'].create({'name': vendor})
                val['partner_id'] = partner_id.id

            # if data is valid, create model object.
            if len(errors) == 0:
                val['asset_seq'] = asset_code
                val['name'] = asset_name
                val['category_id'] = aac[asset_type]
                val['asset_type_id'] = aac[asset_category]
                val['model_name'] = model_name
                val['warranty_date'] = warranty_date
                val['date'] = purchase_date
                val['asset_usage_date'] = usage_date
                val['lst_depr_date'] = lst_depr_date
                val['operating_unit_id'] = branch[pb_code]
                val['current_branch_id'] = branch[cb_code]
                val['sub_operating_unit_id'] = sou[sou_code]
                val['cost_centre_id'] = cc[cc_code]
                val['depr_base_value'] = depr_base_value
                val['value'] = cost_value
                val['value_residual'] = wdv
                val['salvage_value'] = salvage_value
                val['accumulated_value'] = accum_value
                val['currency_id'] = currency[currency_code]
                val['asset_description'] = asset_descr
                val['note'] = note
                val['method'] = cm[cm_code]
                val['method_progress_factor'] = depr_factor
                val['company_id'] = self.env.user.company_id.id
                val['state'] = 'open'
                val['method_period'] = 1
                val['method_time'] = 'number'
                val['is_custom_depr'] = True
                val['depreciation_year'] = int(depr_year) if depr_year else 0
                val['active'] = True
                val['allocation_status'] = True
                val['lst_depr_amount'] = 0.0

                history_line = {
                    'from_branch_id': branch[pb_code],
                    'operating_unit_id': branch[cb_code],
                    'sub_operating_unit_id': sou[sou_code],
                    'cost_centre_id': cc[cc_code],
                    'receive_date': usage_date,
                    'state': 'active'
                }

                if val['method'] != 'no_depreciation':
                    days = (datetime.datetime.strptime(lst_depr_date, '%m/%d/%Y') - datetime.datetime.strptime(
                        usage_date, '%m/%d/%Y'))

                    depreciation_line = {
                        'depreciation_date': lst_depr_date,
                        'days': days.days,
                        'amount': accum_value,
                        'depreciated_value': accum_value,
                        'remaining_value': wdv,
                        'line_type': 'depreciation',
                        'name': 'Opening Depreciation',
                        'sequence': 1,
                        'move_check': True,
                        'move_posted_check': True,
                    }

                    val['depreciation_line_ids'] = [(0, 0, depreciation_line)]

                val['asset_allocation_ids'] = [(0, 0, history_line)]
                self.env['account.asset.asset'].create(val)
                print(line_no)

        end = time.time()
        print('Total Execution Time: {0}'.format(end - start))

        if len(errors) > 0:
            file_path = os.path.join(os.path.expanduser("~"), "FAM_ERR_" + fields.Datetime.now())
            with open(file_path, "w+") as file:
                file.write(errors)
