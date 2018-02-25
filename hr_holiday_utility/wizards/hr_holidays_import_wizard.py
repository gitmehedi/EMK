try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import base64
import csv
import time
from datetime import datetime
from sys import exc_info
from traceback import format_exception

from openerp import api, fields, models, _
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError,Warning

from datetime import timedelta
import datetime


class HrAttendanceImportWizard(models.TransientModel):
    _name = 'hr.holidays.import.wizard'

    aml_data = fields.Binary(string='File')
    aml_fname = fields.Char(string='Filename')
    lines = fields.Binary(
        compute='_compute_lines', string='Input Lines')
    dialect = fields.Binary(
        compute='_compute_dialect', string='Dialect')
    csv_separator = fields.Selection(
        [(',', ', (comma)'), (';', '; (semicolon)')],
        string='CSV Separator', required=True)
    decimal_separator = fields.Selection(
        [('.', '. (dot)'), (',', ', (comma)')],
        string='Decimal Separator',
        default='.')
    codepage = fields.Char(
        string='Code Page',
        default=lambda self: self._default_codepage(),
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

    def _input_fields(self):
        """
        Extend this dictionary if you want to add support for
        fields requiring pre-processing before being added to
        the move line values dict.
        """
        res = {
            'account': {'method': self._handle_account},
            'account_id': {'required': True},
            'debit': {'method': self._handle_debit, 'required': True},
            'credit': {'method': self._handle_credit, 'required': True},
            'partner': {'method': self._handle_partner},
            'product': {'method': self._handle_product},
            'date_maturity': {'method': self._handle_date_maturity},
            'due date': {'method': self._handle_date_maturity},
            'currency': {'method': self._handle_currency},
            'tax account': {'method': self._handle_tax_code},
            'tax_code': {'method': self._handle_tax_code},
            'analytic account': {'method': self._handle_analytic_account},
        }
        return res
  
    def _process_header(self, header_fields):

        self._field_methods = self._input_fields()
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

    def _log_line_error(self, line, msg):
        data = self.csv_separator.join(
            [line[hf] for hf in self._header_fields])
        self._err_log += _(
            "Error when processing line '%s'") % data + ':\n' + msg + '\n\n'

    def _handle_orm_char(self, field, line, move, aml_vals,
                         orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            aml_vals[orm_field] = line[field]

    def _handle_orm_integer(self, field, line, move, aml_vals,
                            orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            val = str2int(
                line[field], self.decimal_separator)
            if val is False:
                msg = _(
                    "Incorrect value '%s' "
                    "for field '%s' of type Integer !"
                    ) % (line[field], field)
                self._log_line_error(line, msg)
            else:
                aml_vals[orm_field] = val

    def _handle_orm_float(self, field, line, move, aml_vals,
                          orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            aml_vals[orm_field] = str2float(
                line[field], self.decimal_separator)

            val = str2float(
                line[field], self.decimal_separator)
            if val is False:
                msg = _(
                    "Incorrect value '%s' "
                    "for field '%s' of type Numeric !"
                    ) % (line[field], field)
                self._log_line_error(line, msg)
            else:
                aml_vals[orm_field] = val

    def _handle_orm_many2one(self, field, line, move, aml_vals,
                             orm_field=False):
        orm_field = orm_field or field
        if not aml_vals.get(orm_field):
            val = str2int(
                line[field], self.decimal_separator)
            if val is False:
                msg = _(
                    "Incorrect value '%s' "
                    "for field '%s' of type Many2One !"
                    "\nYou should specify the database key "
                    "or contact your IT department "
                    "to add support for this field."
                    ) % (line[field], field)
                self._log_line_error(line, msg)
            else:
                aml_vals[orm_field] = val

    def _handle_account(self, field, line, move, aml_vals):
        if not aml_vals.get('account_id'):
            code = line[field]
            if code in self._accounts_dict:
                aml_vals['account_id'] = self._accounts_dict[code]
            else:
                msg = _("Account with code '%s' not found !") % code
                self._log_line_error(line, msg)

    def _handle_debit(self, field, line, move, aml_vals):
        if 'debit' not in aml_vals:
            debit = str2float(line[field], self.decimal_separator)
            aml_vals['debit'] = debit
            self._sum_debit += debit

    def _handle_credit(self, field, line, move, aml_vals):
        if 'credit' not in aml_vals:
            credit = str2float(line[field], self.decimal_separator)
            aml_vals['credit'] = credit
            self._sum_credit += credit

    def _handle_partner(self, field, line, move, aml_vals):
        if not aml_vals.get('partner_id'):
            input = line[field]
            part_mod = self.env['res.partner']
            dom = ['|', ('parent_id', '=', False), ('is_company', '=', True)]
            dom_ref = dom + [('ref', '=', input)]
            partners = part_mod.search(dom_ref)
            if not partners:
                dom_name = dom + [('name', '=', input)]
                partners = part_mod.search(dom_name)
            if not partners:
                msg = _("Partner '%s' not found !") % input
                self._log_line_error(line, msg)
                return
            elif len(partners) > 1:
                msg = _("Multiple partners with Reference "
                        "or Name '%s' found !") % input
                self._log_line_error(line, msg)
                return
            else:
                partner = partners[0]
                aml_vals['partner_id'] = partner.id

    def _handle_product(self, field, line, move, aml_vals):
        if not aml_vals.get('product_id'):
            input = line[field]
            prod_mod = self.env['product.product']
            products = prod_mod.search([
                ('default_code', '=', input)])
            if not products:
                products = prod_mod.search(
                    [('name', '=', input)])
            if not products:
                msg = _("Product '%s' not found !") % input
                self._log_line_error(line, msg)
                return
            elif len(products) > 1:
                msg = _("Multiple products with Internal Reference "
                        "or Name '%s' found !") % input
                self._log_line_error(line, msg)
                return
            else:
                product = products[0]
                aml_vals['product_id'] = product.id

    def _handle_date_maturity(self, field, line, move, aml_vals):
        if not aml_vals.get('date_maturity'):
            due = line[field]
            try:
                datetime.strptime(due, '%Y-%m-%d')
                aml_vals['date_maturity'] = due
            except:
                msg = _("Incorrect data format for field '%s' "
                        "with value '%s', "
                        " should be YYYY-MM-DD") % (field, due)
                self._log_line_error(line, msg)

    def _handle_currency(self, field, line, move, aml_vals):
        if not aml_vals.get('currency_id'):
            name = line[field]
            curr = self.env['res.currency'].search([
                ('name', '=ilike', name)])
            if curr:
                aml_vals['currency_id'] = curr[0].id
            else:
                msg = _("Currency '%s' not found !") % name
                self._log_line_error(line, msg)

    def _handle_tax_code(self, field, line, move, aml_vals):
        if not aml_vals.get('tax_code_id'):
            input = line[field]
            tc_mod = self.env['account.tax.code']
            codes = tc_mod.search([
                ('code', '=', input)])
            if not codes:
                codes = tc_mod.search(
                    [('name', '=', input)])
            if not codes:
                msg = _("%s '%s' not found !") % (field, input)
                self._log_line_error(line, msg)
                return
            elif len(codes) > 1:
                msg = _("Multiple %s entries with Code "
                        "or Name '%s' found !") % (field, input)
                self._log_line_error(line, msg)
                return
            else:
                code = codes[0]
                aml_vals['tax_code_id'] = code.id

    def _handle_analytic_account(self, field, line, move, aml_vals):
        if not aml_vals.get('analytic_account_id'):
            ana_mod = self.env['account.analytic.account']
            input = line[field]
            domain = [('type', '!=', 'view'),
                      ('company_id', '=', move.company_id.id),
                      ('state', 'not in', ['close', 'cancelled'])]
            analytic_accounts = ana_mod.search(
                domain + [('code', '=', input)])
            if len(analytic_accounts) == 1:
                aml_vals['analytic_account_id'] = analytic_accounts.id
            else:
                analytic_accounts = ana_mod.search(
                    domain + [('name', '=', input)])
                if len(analytic_accounts) == 1:
                    aml_vals['analytic_account_id'] = analytic_accounts.id
            if not analytic_accounts:
                msg = _("Invalid Analytic Account '%s' !") % input
                self._log_line_error(line, msg)
            elif len(analytic_accounts) > 1:
                msg = _("Multiple Analytic Accounts found "
                        "that match with '%s' !") % input
                self._log_line_error(line, msg)

    def _process_line_vals(self, line, move, aml_vals):
        """
        Use this method if you want to check/modify the
        line input values dict before calling the move write() method
        """
        if 'name' not in aml_vals:
            aml_vals['name'] = '/'

        if 'debit' not in aml_vals:
            aml_vals['debit'] = 0.0

        if 'credit' not in aml_vals:
            aml_vals['credit'] = 0.0

        if 'partner_id' not in aml_vals:
            # required since otherwise the partner_id
            # of the previous entry is added
            aml_vals['partner_id'] = False

        all_fields = self._field_methods
        required_fields = [x for x in all_fields
                           if all_fields[x].get('required')]
        for rf in required_fields:
            if rf not in aml_vals:
                msg = _("The '%s' field is a required field "
                        "that must be correctly set.") % rf
                self._log_line_error(line, msg)

    def _process_vals(self, move, vals):
        """
        Use this method if you want to check/modify the
        input values dict before calling the move write() method
        """
        dp = self.env['decimal.precision'].precision_get('Account')
        if round(self._sum_debit, dp) != round(self._sum_credit, dp):
            self._err_log += '\n' + _(
                "Error in CSV file, Total Debit (%s) is "
                "different from Total Credit (%s) !"
                ) % (self._sum_debit, self._sum_credit) + '\n'
        return vals

    @api.multi
    def aml_import(self):

        time_start = time.time()
        self._err_log = ''
        move = self.env['hr.holidays.import'].browse(self._context['active_id'])
        self._sum_debit = self._sum_credit = 0.0
        #self._get_orm_fields()
        lines, header = self._remove_leading_lines(self.lines)
        header_fields = csv.reader(
            StringIO.StringIO(header), dialect=self.dialect).next()
        self._header_fields = self._process_header(header_fields)
        reader = csv.DictReader(
            StringIO.StringIO(lines), fieldnames=self._header_fields,
            dialect=self.dialect)
        
        is_success = False
        
        for line in reader:
            temp_vals = {}
            temp_vals['name'] = line['name']
            temp_vals['employee_id'] = line['employee_id']
            temp_vals['holiday_status_id'] = line['holiday_status_id']
            temp_vals['number_of_days'] = line['number_of_days']
            temp_vals['type'] = line['type']
            temp_vals['import_id'] = move.id
             
            temp_pool = self.env['hr.holidays.import.temp']
            temp_pool.create(temp_vals)
             
            """ search employee model with employee ID """
            vals = {}
            vals['name'] = line['name']
            vals['holiday_status_id'] = line['holiday_status_id']
            vals['number_of_days'] = line['number_of_days']
            vals['type'] = line['type']
            vals['import_id'] = move.id

            emp_pool = self.env['hr.employee'].search([('id','=',line['employee_id'])])
            attendance_line_obj = self.env['hr.holidays.import.line']
            attendance_error_obj = self.env['hr.holidays.import.error']
             
            if emp_pool.id is not False:                
                vals['employee_id'] = emp_pool.id
                attendance_line_obj.create(vals)                
            else:

                error_vals = {}
                error_vals['name'] = line['name']
                error_vals['holiday_status_id'] = line['holiday_status_id']
                error_vals['number_of_days'] = line['number_of_days']
                error_vals['type'] = line['type']
                error_vals['import_id'] = move.id

                error_vals['employee_id'] = line['employee_id']
                attendance_error_obj.create(error_vals)
            
            is_success = True
            
        if is_success is True:
            move.action_confirm()

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
