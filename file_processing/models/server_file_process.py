# -*- coding: utf-8 -*-

import os, shutil, xlrd, traceback, logging, json
from datetime import datetime
from contextlib import contextmanager
from odoo import exceptions, models, fields, api, _, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')


class ServerFileProcess(models.Model):
    _name = "server.file.process"
    _description = "Configuration of SFTP File Processing"
    _inherit = "mail.thread"

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Cannot duplicate a configuration."),
        ("days_to_keep_positive", "CHECK(days_to_keep >= 0)",
         "I cannot remove backups from the future. Ask Doc for that."),
    ]

    name = fields.Char(string="Name", required=True, track_visibility='onchange')
    folder = fields.Char(default=lambda self: self._default_path(), string="Local Folder Path",
                         track_visibility='onchange')
    days_to_keep = fields.Integer(required=True, default=0, )
    method = fields.Selection(selection=[("local", "Local disk"), ("sftp", "Remote SFTP Server")], default="local",
                              required=True, track_visibility='onchange')

    source_path = fields.Char(string="Folder Path", required=True, track_visibility='onchange')
    source_sftp_host = fields.Char(string='SFTP Server', track_visibility='onchange')
    source_sftp_port = fields.Integer(string="SFTP Port", default=22, track_visibility='onchange')
    source_sftp_user = fields.Char(string='Username', track_visibility='onchange')
    source_sftp_password = fields.Char(string="SFTP Password")
    source_sftp_private_key = fields.Char(string="Primary Key Location", track_visibility='onchange')

    dest_path = fields.Char(string="Folder Path", required=True, track_visibility='onchange')
    dest_sftp_host = fields.Char(string='SFTP Server', track_visibility='onchange')
    dest_sftp_port = fields.Integer(string="SFTP Port", default=22, track_visibility='onchange')
    dest_sftp_user = fields.Char(string='Username', track_visibility='onchange')
    dest_sftp_password = fields.Char(string="SFTP Password")
    dest_sftp_private_key = fields.Char(string="Primary Key Location", track_visibility='onchange')

    @api.constrains('source_path', 'dest_path', 'folder')
    def onchange_path(self):
        if self.method == 'local':
            if self.source_path:
                if not os.path.exists(self.source_path):
                    raise ValidationError(_('Source Path [{0}] doesn\'t exists.'.format(self.source_path)))
            if self.dest_path:
                if not os.path.exists(self.dest_path):
                    raise ValidationError(_('Destination Path [{0}] doesn\'t exists.'.format(self.dest_path)))

        if self.method == 'sftp':
            with self.sftp_connection('source') as source:
                if self.source_path:
                    if not source.exists(self.source_path):
                        raise ValidationError(_('Source Path [{0}] doesn\'t exists.'.format(self.source_path)))

            with self.sftp_connection('destination') as destination:
                if self.dest_path:
                    if not destination.exists(self.dest_path):
                        raise ValidationError(_('Destination Path [{0}] doesn\'t exists.'.format(self.dest_path)))

            if self.folder:
                if not os.path.exists(self.folder):
                    raise ValidationError(_('Local Path [{0}] doesn\'t exists.'.format(self.folder)))

    @api.onchange('method')
    def onchange_name(self):
        if self.method == 'local':
            self.source_path = None
            self.source_sftp_host = None
            self.source_sftp_port = None
            self.source_sftp_user = None
            self.source_sftp_password = None
            self.source_sftp_private_key = None
            self.dest_path = None
            self.dest_sftp_host = None
            self.dest_sftp_port = None
            self.dest_sftp_user = None
            self.dest_sftp_password = None
            self.dest_sftp_private_key = None

    @api.model
    def _default_path(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.expanduser('~')

    @api.multi
    @api.depends("folder", "method", "source_sftp_host", "source_sftp_port", "source_sftp_user")
    def _compute_name(self):
        for rec in self:
            if rec.method == "local":
                rec.name = "%s @ localhost" % rec.folder
            elif rec.method == "sftp":
                rec.name = "sftp://%s@%s:%d%s" % (
                    rec.source_sftp_user, rec.source_sftp_host, rec.source_sftp_port, rec.folder)

    @api.multi
    @api.constrains("folder", "method")
    def _check_folder(self):
        """Do not use the filestore or you will backup your backups."""
        for s in self:
            if (s.method == "local" and
                    s.folder.startswith(
                        tools.config.filestore(self.env.cr.dbname))):
                raise exceptions.ValidationError(
                    _("Do not save backups on your filestore, or you will "
                      "backup your backups too!"))

    @api.multi
    def action_sftp_test_connection(self):
        """Check if the SFTP settings are correct."""

        if self.env.context.get('target') == 'source':
            connection = 'source'
        else:
            connection = 'destination'

        try:
            # Just open and close the connection
            with self.sftp_connection(connection):
                raise exceptions.Warning(_("Connection Test Succeeded!"))
        except (pysftp.CredentialException,
                pysftp.ConnectionException,
                pysftp.SSHException):
            _logger.info("Connection Test Failed!", exc_info=True)
            raise exceptions.Warning(_("Connection Test Failed!"))

    @api.one
    def directory_check(self, dirs):
        for dir in dirs:
            if not os.path.isdir(dir):
                try:
                    os.makedirs(dir)
                except OSError:
                    pass

    @api.multi
    def sftp_connection(self, connection):
        """Return a new SFTP connection with found parameters."""
        self.ensure_one()
        if connection == 'source':
            params = {
                "host": self.source_sftp_host,
                "username": self.source_sftp_user,
                "port": self.source_sftp_port,
            }
            _logger.debug(
                "Trying to connect to sftp://%(username)s@%(host)s:%(port)d",
                extra=params)
            if self.source_sftp_private_key:
                params["private_key"] = self.source_sftp_private_key
                if self.source_sftp_password:
                    params["private_key_pass"] = self.source_sftp_password
            else:
                params["password"] = self.source_sftp_password
        else:
            params = {
                "host": self.dest_sftp_host,
                "username": self.dest_sftp_user,
                "port": self.dest_sftp_port,
            }
            _logger.debug(
                "Trying to connect to sftp://%(username)s@%(host)s:%(port)d",
                extra=params)
            if self.dest_sftp_private_key:
                params["private_key"] = self.dest_sftp_private_key
                if self.dest_sftp_password:
                    params["private_key_pass"] = self.dest_sftp_password
            else:
                params["password"] = self.dest_sftp_password

        return pysftp.Connection(**params)

    @api.multi
    def action_backup(self):

        for rec in self.filtered(lambda r: r.method == "local"):
            dirs = [rec.source_path, rec.dest_path]
            self.directory_check(dirs)

            files = filter(lambda x: x.endswith('.txt'), os.listdir(rec.source_path))
            for file in files:

                if os.path.splitext(file)[1] in ['.txt']:
                    source_path = os.path.join(rec.source_path, file)
                    dest_path = os.path.join(rec.dest_path, file)

                    journal = rec.create_journal(file)
                    if journal:
                        if shutil.move(source_path, dest_path):
                            raise ValidationError(_('Please check path configuration.'))

        for rec in self.filtered(lambda r: r.method == "sftp"):
            with self.sftp_connection('source') as source:
                with self.sftp_connection('destination') as destination:
                    dirs = [rec.folder, rec.source_path, rec.dest_path]
                    self.directory_check(dirs)
                    files = filter(lambda x: x.endswith('.txt'), source.listdir(rec.source_path))
                    for file in files:
                        source_path = os.path.join(rec.source_path, file)
                        dest_path = os.path.join(rec.dest_path, file)
                        local_path = os.path.join(rec.folder, file)

                        source.get(source_path, localpath=local_path, preserve_mtime=True)
                        journal = rec.create_journal(file, {'source': source, 'dest': destination})

                        if journal:
                            if destination.put(local_path, dest_path):
                                if not source.unlink(source_path):
                                    os.remove(local_path)
                                else:
                                    raise ValidationError(_('Please check path configuration.'))
                            else:
                                raise ValidationError(_('Please check path configuration.'))

    def get_file_path(self, file):
        path = {}
        if self.method == 'local':
            path['folder'] = os.path.join(self.folder, file)
            path['source'] = os.path.join(self.source_path, file)
            path['destination'] = os.path.join(self.dest_path, file)
        else:
            path['folder'] = os.path.join(self.folder, file)
            path['source'] = os.path.join(self.source_path, file)
            path['destination'] = os.path.join(self.dest_path, file)

        return path

    def preprocess(self, data):
        filter = data.split('.')
        return filter[0].strip() if len(filter) > 0 else None

    def data_mapping(self, data):
        data = data.split('|')
        glcc_struc = [3, 3, 1, 5, 3, 2, 2, 3]
        date_struc = [2, 2, 4, 2, 2, 2]
        glcc_name = ['BRANCH', 'CURRENCY', 'SEGMENT', 'COMP_1', 'COMP_2', 'AC', 'SC', 'COST_CENTRE']

        data[9] = dict(zip(glcc_name, self.strslice(data[9], glcc_struc)))
        data[0] = self.format_data(self.strslice(data[0] + data[2], date_struc))
        data[1] = self.format_data(self.strslice(data[1] + '000000', date_struc))
        data[13] = self.format_data(self.strslice(data[13] + '000000', date_struc))

        keys = ['POSTING-DATE', 'SYSTEM-DATE', 'POSTING-TIME', 'SOURCE', 'JOURNAL-NBR', 'JOURNAL-SEQ',
                'SOC', 'BRCH', 'FCY-CODE', 'GL-CLASS-CODE', 'DESC-TRCODE-6', 'DESC-TEXT-24', 'POSTING-IND',
                'TRANS-DATE', 'LCY-AMT',
                'FCY-AMT', 'REVERSAL-CODE', 'REVERSAL-DATE', 'REFERENCE', 'SOURCE-APPLN', 'PS-JOURNAL-ID',
                'PS-JOURNAL-NBR', 'CNTL-CENTRE']

        return dict(zip(keys, data[:len(data)]))

    @api.multi
    def format_data(self, date):
        if len(date) == 6:
            try:
                data = "{0}-{1}-{2} {3}:{4}:{5}".format(date[1], date[0], date[2], date[3], date[4], date[5])
                date_con = datetime.strptime(data, '%m-%d-%Y %H:%M:%S')
            except Exception:
                date_con = False

            if date_con:
                return date_con
        return None

    @api.multi
    def strslice(self, pattern, lists):
        first, last = 0, 0
        values = []
        for val in lists:
            last += val
            values.append(pattern[first:last])
            first += val
        return values

    @api.multi
    def create_journal(self, file, conn={}):
        errors, response = [], False
        path = self.get_file_path(file)
        source_path = path['source'] if self.method == 'local' else path['folder']
        with open(source_path, 'r') as file_ins:
            moves = {}
            index = 0
            for worksheet_index in file_ins:
                index += 1

                if len(worksheet_index) > 2:
                    rec = self.data_mapping(worksheet_index)

                    journal_no = rec['JOURNAL-NBR']
                    journal_type = 'CBS Invoices'
                    journal = self.env['account.journal'].search([('name', '=', journal_type)])
                    if not journal:
                        raise Warning(_('[Wanring] Journal type [{0}]is not available.'.format(journal_type)))
                    if journal_no not in moves:
                        moves[journal_no] = {
                            'journal_id': journal.id,
                            'date': rec['POSTING-DATE'],
                            'is_cbs': True,
                            'ref': journal_no,
                            'line_ids': [],
                        }
                    name = rec['DESC-TEXT-24'].strip()
                    if not name:
                        errors.append(
                            (0, 0, {'line_no': index, 'details': 'DESC-TEXT-24 [{0}] has invalid value'.format(name)}))

                    amount = float(rec['LCY-AMT'][:14] + '.' + rec['LCY-AMT'][14:17])
                    if not amount:
                        errors.append(
                            (0, 0, {'line_no': index, 'details': 'LCY-AMT [{0}] has invalid value'.format(amount)}))

                    posting_date = rec['POSTING-DATE']
                    if not posting_date:
                        errors.append(
                            (0, 0, {'line_no': index, 'details': 'POSTING-DATE or POSTING-TIME has invalid value'}))

                    system_date = rec['SYSTEM-DATE']
                    if not system_date:
                        errors.append((0, 0, {'line_no': index, 'details': 'SYSTEM-DATE has invalid value'}))

                    trans_date = rec['TRANS-DATE']
                    if not trans_date:
                        errors.append((0, 0, {'line_no': index, 'details': 'TRANS-DATE has invalid value'}))

                    branch = rec['GL-CLASS-CODE']['BRANCH']
                    branch_id = self.env['operating.unit'].search([('code', '=', branch)])
                    if not branch_id:
                        errors.append(
                            (0, 0, {'line_no': index, 'details': 'BRANCH [{0}] has invalid value'.format(branch)}))

                    currency = rec['GL-CLASS-CODE']['CURRENCY']
                    currency_id = self.env['res.currency'].search([('code', '=', currency)])
                    if not currency_id:
                        errors.append(
                            (0, 0, {'line_no': index, 'details': 'CURRENCY [{0}]  has invalid value'.format(currency)}))

                    segment = rec['GL-CLASS-CODE']['SEGMENT']
                    segment_id = self.env['segment'].search([('code', '=', segment)])
                    if not segment_id:
                        errors.append(
                            (0, 0, {'line_no': index, 'details': 'SEGMENT [{0}]  has invalid value'.format(segment)}))

                    ac = rec['GL-CLASS-CODE']['AC']
                    ac_id = self.env['acquiring.channel'].search([('code', '=', ac)])
                    if not ac_id:
                        errors.append((0, 0, {'line_no': index, 'details': 'AC [{0}]  has invalid value'.format(ac)}))

                    sc = rec['GL-CLASS-CODE']['SC']
                    sc_id = self.env['servicing.channel'].search([('code', '=', sc)])
                    if not sc_id:
                        errors.append((0, 0, {'line_no': index, 'details': 'SC [{0}]  has invalid value'.format(sc)}))

                    cost_centre = rec['GL-CLASS-CODE']['COST_CENTRE']
                    cost_centre_id = self.env['account.analytic.account'].search([('code', '=', cost_centre)])
                    if not cost_centre_id:
                        errors.append(
                            (0, 0,
                             {'line_no': index, 'details': 'COST_CENTRE [{0}]  has invalid value'.format(cost_centre)}))

                    if rec['GL-CLASS-CODE']['COMP_1'] and rec['GL-CLASS-CODE']['COMP_2']:
                        comp_1 = rec['GL-CLASS-CODE']['COMP_1']
                        comp_2 = rec['GL-CLASS-CODE']['COMP_2']

                        account = comp_1 + comp_2
                        account_id = self.env['account.account'].search([('code', '=', account)])
                        if not account_id:
                            errors.append(
                                (0, 0, {'line_no': index,
                                        'details': 'COMP_1 or COMP_2 [{0}] has invalid value'.format(account)}))

                    if rec['JOURNAL-SEQ'] == '01':
                        line = {
                            'name': name,
                            'account_id': account_id.id,
                            'credit': amount,
                            'debit': 0.0,
                            'journal_id': journal.id,
                            'analytic_account_id': cost_centre_id.id,
                            'currency_id': currency_id.id,
                            'segment_id': segment_id.id,
                            'acquiring_channel_id': ac_id.id,
                            'servicing_channel_id': sc_id.id,
                            'operating_unit_id': branch_id.id,
                        }
                        moves[journal_no]['line_ids'].append((0, 0, line))

                    if rec['JOURNAL-SEQ'] == '02':
                        line = {
                            'name': name,
                            'account_id': account_id.id,
                            'credit': 0.0,
                            'debit': amount,
                            'journal_id': journal.id,
                            'analytic_account_id': cost_centre_id.id,
                            'currency_id': currency_id.id,
                            'segment_id': segment_id.id,
                            'acquiring_channel_id': ac_id.id,
                            'servicing_channel_id': sc_id.id,
                            'operating_unit_id': branch_id.id,
                        }

                        moves[journal_no]['line_ids'].append((0, 0, line))

            if len(errors) > 0:
                self.env['server.file.error'].create({'file_path': source_path,
                                                      'line_ids': errors,
                                                      'ftp_ip': self.source_sftp_host})
            else:
                try:
                    for key in moves:
                        move_obj = self.env['account.move'].create(moves[key])
                        if move_obj.state == 'draft':
                            move_obj.post()
                    return True
                except Exception:
                    self.env['server.file.error'].create({'file_path': source_path,
                                                          'errors': 'Unknown Error. Please check your file.',
                                                          'ftp_ip': 'localhost'})

        return False

    @api.model
    def action_backup_all(self):
        """Run all scheduled backups."""
        return self.search([]).action_backup()

    @api.multi
    @contextmanager
    def backup_log(self):
        """Log a backup result."""
        try:
            _logger.info("Starting database backup: %s", self.name)
            yield
        except:
            _logger.exception("Database backup failed: %s", self.name)
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(
                "<p>%s</p><pre>%s</pre>" % (
                    _("Database backup failed."),
                    escaped_tb),
                subtype=self.env.ref(
                    "file_processing.mail_message_subtype_failure"
                ),
            )
        else:
            _logger.info("Database backup succeeded: %s", self.name)
            self.message_post(_("Database backup succeeded."))

    @api.multi
    @contextmanager
    def cleanup_log(self):
        """Log a possible cleanup failure."""
        self.ensure_one()
        try:
            _logger.info("Starting cleanup process after database backup: %s",
                         self.name)
            yield
        except:
            _logger.exception("Cleanup of old database backups failed: %s")
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(
                "<p>%s</p><pre>%s</pre>" % (
                    _("Cleanup of old database backups failed."),
                    escaped_tb),
                subtype=self.env.ref("file_processing.failure"))
        else:
            _logger.info("Cleanup of old database backups succeeded: %s",
                         self.name)

    @api.one
    def move_file_src_to_des(self, source_con):
        dest_con = ''
        shutil.move(source_con, dest_con)

    @api.one
    def get_formatted_data(self, var_worksheet):
        worksheet_col = []  # list of columns
        for col in range(var_worksheet.ncols):
            worksheet_col.append(str(var_worksheet.cell(0, col).value))

        formatted_data = []  # collection of dict
        for row in range(1, var_worksheet.nrows):
            my_dict = {}
            for col in range(var_worksheet.ncols - 1):
                my_dict[worksheet_col[col]] = str(var_worksheet.cell(row, col).value)
            formatted_data.append(my_dict)

        return formatted_data
