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

RENT_TYPE = {'General Rent': 'general', 'Govt. Premise Rent': 'govt_premise'}
BILLING_PERIOD = {'Monthly': 'monthly', 'Yearly': 'yearly'}
PAYMENT_TYPE = {'CASA': 'casa', 'Credit Account': 'credit'}


class GBSFileImportWizard(models.TransientModel):
    _name = 'gbs.rent.data.migration.wizard'

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
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            is_valid = False

        return is_valid

    @staticmethod
    def convert_amount_str(amount_str):
        amount = 0.0
        if len(amount_str) > 0:
            amount = abs(float(amount_str))

        return amount

    @staticmethod
    def check_leading_zero(code_str):
        code = code_str
        if len(code) == 1:
            code = '00' + code
        if len(code) == 2:
            code = '0' + code

        return code

    @api.multi
    def get_existing_data(self):
        partner = {val.name.strip().upper(): val.id for val in self.env['res.partner'].search([('supplier', '=', True), ('active', '=', True)])}
        product = {val.name.strip().upper(): val.id for val in self.env['product.product'].search([('active', '=', True)])}
        aa = {val.code: val.id for val in self.env['account.account'].search([('active', '=', True)])}
        sequence = {val.account_id.code + '-' + val.code: val.id for val in self.env['sub.operating.unit'].search([('active', '=', True)])}
        branch = {val.code: val.id for val in self.env['operating.unit'].search([('active', '=', True)])}
        cc = {val.code: val.id for val in self.env['account.analytic.account'].search([('active', '=', True)])}
        currency = {val.code: val.id for val in self.env['res.currency'].search([('active', '=', True)])}
        vat = {val.name: val.id for val in self.env['account.tax'].search([('is_vat', '=', True), ('active', '=', True)])}
        tds = {val.name: val.id for val in self.env['account.tax'].search([('is_tds', '=', True), ('active', '=', True)])}

        return partner, product, aa, sequence, branch, cc, currency, vat, tds

    @api.multi
    def aml_import(self):
        start = time.time()
        if not self.lines:
            raise ValidationError(_('Please Select File.'))

        index = 0
        errors, data_list = "", []

        self._err_log = ''
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(StringIO.StringIO(lines), fieldnames=self._header_fields, dialect=self.dialect)

        allow_header = [
            'reference',
            'vendor',
            'service/product',
            'gl account',
            'sequence',
            'branch',
            'start date',
            'end date',
            'additional service',
            'rent type',
            'billing period',
            'vat',
            'tds',
            'area (ft)',
            'rate',
            'approved advance',
            'adjusted amount',
            'adjustment value',
            'service value',
            'ad. service value',
            'particulars',
            'cost centre',
            'payment to',
            'credit account',
            'credit sequence',
            'credit branch',
            'currency'
        ]

        # retrieve existing data from database
        partner, product, aa, sequence, branch, cc, currency, vat, tds = self.get_existing_data()

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
            is_valid = True
            val = {}

            reference = line['reference'].strip()
            vendor = line['vendor'].strip().upper()
            product_name = line['service/product'].strip().upper()
            acc_code = line['gl account'].strip()
            seq_code = line['sequence'].strip()
            branch_code = self.check_leading_zero(line['branch'].strip())
            start_date = line['start date'].strip()
            end_date = line['end date'].strip()
            additional_service = line['additional service'].strip().upper()
            rent_type = line['rent type'].strip()
            billing_period = line['billing period'].strip()
            vat_name = line['vat'].strip()
            tds_name = line['tds'].strip()
            area = self.convert_amount_str(line['area (ft)'].strip().replace(',', ''))
            rate = self.convert_amount_str(line['rate'].strip().replace(',', ''))
            advance_amount = self.convert_amount_str(line['approved advance'].strip().replace(',', ''))
            adjusted_amount = self.convert_amount_str(line['adjusted amount'].strip().replace(',', ''))
            adjustment_value = self.convert_amount_str(line['adjustment value'].strip().replace(',', ''))
            service_value = self.convert_amount_str(line['service value'].strip().replace(',', ''))
            additional_service_value = self.convert_amount_str(line['ad. service value'].strip().replace(',', ''))
            particulars = line['particulars'].strip()
            cc_code = self.check_leading_zero(line['cost centre'].strip())
            payment_type = line['payment to'].strip()
            cr_acc_code = line['credit account'].strip()
            cr_seq_code = line['credit sequence'].strip()
            cr_branch_code = self.check_leading_zero(line['credit branch'].strip())
            currency_code = line['currency'].strip()

            if vendor not in partner.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Vendor [{0}] invalid value'.format(line['vendor'].strip())) + '\n'

            if vendor in partner.keys() and PAYMENT_TYPE[payment_type] == 'casa':
                vendor_obj = self.env['res.partner'].search([('id', '=', partner[vendor])])
                if not vendor_obj.vendor_bank_acc:
                    is_valid = False
                    errors += self.format_error(line_no, 'Vendor Bank Account of {0} [{1}] invalid value'.format(vendor, vendor_obj.vendor_bank_acc)) + '\n'

            if product_name not in product.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Service/Product [{0}] invalid value'.format(line['service/product'].strip())) + '\n'

            if acc_code not in aa.keys():
                is_valid = False
                errors += self.format_error(line_no, 'GL Account [{0}] invalid value'.format(acc_code)) + '\n'

            if acc_code in aa.keys():
                account_id = self.env['account.account'].search([('id', '=', aa[acc_code])])
                if account_id.reconcile and not reference:
                    is_valid = False
                    errors += self.format_error(line_no, 'Reconcile Reference [{0}] invalid value'.format(reference)) + '\n'

            if seq_code not in sequence.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Sequence [{0}] invalid value'.format(seq_code)) + '\n'

            if branch_code not in branch.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Branch [{0}] invalid value'.format(branch_code)) + '\n'

            if not self.date_validate(start_date):
                is_valid = False
                errors += self.format_error(line_no, 'Start Date [{0}] invalid value'.format(start_date)) + '\n'

            # if not self.date_validate(end_date):
            #     is_valid = False
            #     errors += self.format_error(line_no, 'End Date [{0}] invalid value'.format(end_date)) + '\n'

            if additional_service and additional_service not in product.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Additional Service [{0}] invalid value'.format(line['additional service'].strip())) + '\n'

            if rent_type not in RENT_TYPE.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Rent Type [{0}] invalid value'.format(rent_type)) + '\n'

            if billing_period not in BILLING_PERIOD.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Billing Period [{0}] invalid value'.format(billing_period)) + '\n'

            if vat_name and vat_name not in vat.keys():
                is_valid = False
                errors += self.format_error(line_no, 'VAT [{0}] invalid value'.format(vat_name)) + '\n'

            if tds_name and tds_name not in tds.keys():
                is_valid = False
                errors += self.format_error(line_no, 'TDS [{0}] invalid value'.format(tds_name)) + '\n'

            if service_value < 0:
                is_valid = False
                errors += self.format_error(line_no, 'Service Value [{0}] invalid value'.format(service_value)) + '\n'

            if adjustment_value > service_value:
                is_valid = False
                errors += self.format_error(line_no, 'Adjustment Value can not be greater than Service Value') + '\n'

            if adjustment_value > advance_amount:
                is_valid = False
                errors += self.format_error(line_no, 'Adjustment Value can not be greater than Approved Advance') + '\n'

            if cc_code not in cc.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Cost Center [{0}] invalid value'.format(cc_code)) + '\n'

            if payment_type not in PAYMENT_TYPE.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Payment Type [{0}] invalid value'.format(payment_type)) + '\n'

            if PAYMENT_TYPE[payment_type] == 'credit':
                if cr_acc_code not in aa.keys():
                    is_valid = False
                    errors += self.format_error(line_no, 'Credit Account [{0}] invalid value'.format(cr_acc_code)) + '\n'

                if cr_seq_code not in sequence.keys():
                    is_valid = False
                    errors += self.format_error(line_no, 'Credit Sequence [{0}] invalid value'.format(cr_seq_code)) + '\n'

                if cr_branch_code not in branch.keys():
                    is_valid = False
                    errors += self.format_error(line_no, 'Credit Branch [{0}] invalid value'.format(cr_branch_code)) + '\n'

            if currency_code not in currency.keys():
                is_valid = False
                errors += self.format_error(line_no, 'Currency Code [{0}] invalid value'.format(currency_code)) + '\n'

            if is_valid:
                val['name'] = reference
                val['partner_id'] = partner[vendor]
                val['description'] = particulars
                val['product_id'] = product[product_name]
                val['account_id'] = aa[acc_code]
                val['sub_operating_unit_id'] = sequence[seq_code]
                val['operating_unit_id'] = branch[branch_code]
                val['account_analytic_id'] = cc[cc_code]
                val['start_date'] = start_date
                val['end_date'] = end_date
                val['additional_service'] = product[additional_service] if additional_service else False
                val['rent_type'] = RENT_TYPE[rent_type]
                val['billing_period'] = BILLING_PERIOD[billing_period]
                val['vat_id'] = vat[vat_name] if vat_name else False
                val['tds_id'] = tds[tds_name] if tds_name else False
                val['area'] = area
                val['rate'] = rate
                val['advance_amount'] = advance_amount
                val['adjusted_amount'] = adjusted_amount
                val['adjustment_value'] = adjustment_value
                val['service_value'] = service_value
                val['additional_service_value'] = additional_service_value
                val['payment_type'] = PAYMENT_TYPE[payment_type]
                val['currency_id'] = currency[currency_code]
                val['company_id'] = self.env.user.company_id.id
                val['active'] = True
                val['state'] = 'approve'
                val['type'] = 'multi'
                val['is_bulk_data'] = True

                if val['payment_type'] == 'credit':
                    val['credit_account_id'] = aa[cr_acc_code]
                    val['credit_sub_operating_unit_id'] = sequence[cr_seq_code]
                    val['credit_operating_unit_id'] = branch[cr_branch_code]

                data_list.append(val)

        if len(errors) == 0:
            for item in data_list:
                rent_id = self.env['vendor.advance'].create(item)
                if not item['name']:
                    name = rent_id.get_seq()
                    rent_id.write({'name': name})
        else:
            file_path = os.path.join(os.path.expanduser("~"), "RENT_ERR_" + fields.Datetime.now())
            with open(file_path, "w+") as file:
                file.write(errors)

            raise Warning('You have invalid data and a file has been created for invalid data.')
