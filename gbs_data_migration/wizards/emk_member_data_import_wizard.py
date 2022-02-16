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
from odoo.addons.opa_utility.helper.utility import Utility,Message


class EMKMemberDataImportWizard(models.TransientModel):
    _name = 'emk.member.data.import.wizard'

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
        mc = {val.name: val.id for val in self.env['membership.membership_category'].search([('status', '=', True)])}
        product = {val.name: val.id for val in self.env['product.template'].search([('active', '=', True)])}
        occupation = {val.name: val.id for val in self.env['member.occupation'].search([('status', '=', True)])}
        msi = {val.name: val.id for val in self.env['member.subject.interest'].search([('status', '=', True)])}
        mcer = {val.name: val.id for val in self.env['member.certification'].search([('status', '=', True)])}
        partner = {val.email: val.id for val in self.env['res.partner'].search([])}

        return mc, product, occupation, msi, mcer, partner

    @api.multi
    def data_import(self):
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

        allow_header = ['id number',
                        'membership categories',
                        'membership status',
                        'joining date',
                        'membership expire',
                        'first name',
                        'middle name',
                        'last name',
                        'date of birth',
                        'gender',
                        'phone',
                        'address',
                        'city',
                        'zip',
                        'mobile',
                        'email',
                        'occupation',
                        'last or current place of study',
                        'highest certification achieved',
                        'place of study',
                        'current employer',
                        'field of study',
                        ]

        # retrieve existing data from database
        mc, product, moc, msi, mcer, partner = self.get_existing_data()

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

            id_number = line['id number'].strip()
            membership_categories = line['membership categories'].strip()
            membership_status = line['membership status'].strip()
            joining_date = Utility.date_format(line['joining date'].strip())
            membership_expire = Utility.date_format(line['membership expire'].strip())
            first_name = line['first name'].strip()
            middle_name = line['middle name'].strip()
            last_name = line['last name'].strip()
            date_of_birth = Utility.date_format(line['date of birth'].strip())
            gender = line['gender'].strip()
            phone = line['phone'].strip()
            address = line['address'].strip()
            city = line['city'].strip()
            zip = line['zip'].strip()
            mobile = line['mobile'].strip()
            email = line['email'].strip()
            occupation = line['occupation'].strip()
            occupation_other = ''
            last_or_curr = line['last or current place of study'].strip()
            hca = line['highest certification achieved'].strip()
            field_of_study = line['field of study'].strip()
            place_of_study = line['place of study'].strip()
            current_employer = line['current employer'].strip()


            mc, product, moc, msi, mcer, partner
            if not id_number:
                errors += self.format_error(line_no, 'ID [{0}] invalid value'.format(id_number))

            if membership_categories not in mc.keys():
                errors += self.format_error(line_no,
                                            'Membership Category [{0}] invalid value'.format(membership_categories))

            if occupation not in moc.keys():
                occupation = ''
                occupation_other = occupation

            if hca not in mcer.keys():
                hca = mcer['Other']
            else:
                hca = mcer[hca]

            if len(errors) == 0:
                val['member_sequence'] = id_number
                val['firstname'] = first_name
                val['middlename'] = middle_name
                val['lastname'] = last_name
                val['birth_date'] = date_of_birth
                val['phone'] = phone
                val['street'] = address
                val['city'] = city
                val['zip'] = zip
                val['mobile'] = mobile
                val['gender'] = gender.lower()
                val['email'] = email
                val['occupation'] = moc[occupation] if occupation else ''
                val['occupation_other'] = occupation_other
                val['last_place_of_study'] = last_or_curr
                val['highest_certification'] = hca
                val['place_of_study'] = place_of_study
                val['field_of_study'] = field_of_study
                val['current_employee'] = current_employer
                val['state'] = 'member'
                val['free_member'] = True
                val['membership_start'] = joining_date
                val['membership_last_start'] = joining_date
                val['membership_stop'] = membership_expire
                val['membership_status'] = membership_status.lower()

                state = 'paid'
                if 'Honorary Member':
                    state = 'free'

                member_cat = self.env['product.template'].search(
                    [('membership_category_id', '=', mc[membership_categories]), ('active', '=', True)])
                member_line = {
                    'date': joining_date,
                    'date_from': joining_date,
                    'date_to': membership_expire,
                    'state': state,
                    'membership_id': member_cat.id,
                    'member_price': member_cat.list_price
                }

                if email in partner.keys():
                    exist = self.env['res.partner'].search([('email', '=', email)])[0]
                    exist.write(val)
                    member_line['partner'] = exist.id
                    self.env['membership.membership_line'].create(member_line)
                    print index, "-------UPDATE---------", email
                else:
                    val['member_lines'] = [(0, 0, member_line)]
                    self.env['res.partner'].create(val)
                    print index,"-------CREATE---------", email
        if len(errors) > 0:
            file_path = os.path.join(os.path.expanduser("~"), "FAM_ERR_" + fields.Datetime.now())
            with open(file_path, "w+") as file:
                file.write(errors)
        else:
            query = """UPDATE RES_PARTNER RP
                    SET MEMBERSHIP_START = SUB.DATE,
                        MEMBERSHIP_LAST_START = SUB.DATE,
                        MEMBERSHIP_STOP = SUB.DATE_TO
                    FROM
                        (SELECT * FROM MEMBERSHIP_MEMBERSHIP_LINE) AS SUB
                    WHERE RP.ID = SUB.PARTNER
                        AND RP.STATE = 'member'
                        AND FREE_MEMBER = TRUE"""
            self.env.cr.execute(query)

