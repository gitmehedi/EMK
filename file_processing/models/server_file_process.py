# -*- coding: utf-8 -*-

import os, shutil, xlrd, traceback, logging, json
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

            files = filter(lambda x: x.endswith('.xls'), os.listdir(rec.source_path))
            for file in files:
                if os.path.splitext(file)[1] in ['.xls']:
                    journal = rec.create_journal(file)
                    if journal:
                        if not shutil.move(os.path.join(rec.source_path, file), os.path.join(rec.dest_path, file)):
                            raise ValidationError(_('Please check path configuration.'))

        with self.sftp_connection('source') as source:
            with self.sftp_connection('destination') as destination:
                for rec in self.filtered(lambda r: r.method == "sftp"):
                    dirs = [rec.folder, rec.source_path, rec.dest_path]
                    self.directory_check(dirs)
                    files = filter(lambda x: x.endswith('.xls'), source.listdir(rec.source_path))
                    for file in files:
                        source_path = os.path.join(rec.source_path, file)
                        dest_path = os.path.join(rec.dest_path, file)
                        local_path = os.path.join(rec.folder, file)

                        source.get(source_path, localpath=local_path, preserve_mtime=True)
                        journal = rec.create_journal(file, {'source': source, 'dest': destination})

                        if journal:
                            if destination.put(local_path, dest_path):
                                if source.unlink(source_path):
                                    os.remove(local_path)
                                raise ValidationError(_('Please check path configuration.'))
                            else:
                                raise ValidationError(_('Please check path configuration.'))

    def get_file_path(self, file, loc='s'):
        if self.method == 'local':
            if loc == 's':
                return os.path.join(self.source_path, file)
            else:
                return os.path.join(self.dest_path, file)
        else:
            return os.path.join(self.folder, file)

    def preprocess(self, data):
        filter = data.split('.')
        return filter[0].strip() if len(filter) > 0 else None

    @api.one
    def create_journal(self, file, conn={}):
        source_path = self.get_file_path(file)
        response = False
        if len(conn) > 0:
            dest_path = self.get_file_path(file, loc='d')
        else:
            dest_path = self.get_file_path(self, filegit )

        file_ins = xlrd.open_workbook(source_path)
        errors = []

        for worksheet_index in range(file_ins.nsheets):
            records = self.get_formatted_data(file_ins.sheet_by_index(worksheet_index))
            moves = {}
            for rec in records[0]:
                index = records[0].index(rec) + 2
                trn_no = int(self.preprocess(rec['TRN_NO']))
                journal = self.env['account.journal'].search([('name', '=', 'Customer Invoices')])
                if trn_no not in moves:
                    moves[trn_no] = {
                        'journal_id': journal.id,
                        'date': fields.Date.today(),
                        'line_ids': [],
                    }

                name = rec['BATCH_DESCRIPTION'].strip()
                if not name:
                    errors.append(
                        {'line_no': index, 'details': 'BATCH_DESCRIPTION [{0}]has invalid value'.format(name)})

                amount = float(rec['TRANSACTION_AMOUNT'].strip())
                if not amount:
                    errors.append(
                        {'line_no': index, 'details': 'TRANSACTION_AMOUNT [{0}] has invalid value'.format(amount)})

                currency = self.preprocess(rec['CURRENCY'])
                currency_id = self.env['res.currency'].search([('code', '=', currency)])
                if not currency_id:
                    errors.append({'line_no': index, 'details': 'CURRENCY [{0}]  has invalid value'.format(currency)})

                segment = self.preprocess(rec['SEGMENT'])
                segment_id = self.env['segment'].search([('code', '=', segment)])
                if not segment_id:
                    errors.append({'line_no': index, 'details': 'SEGMENT [{0}]  has invalid value'.format(segment)})

                ac = self.preprocess(rec['AC'])
                ac_id = self.env['acquiring.channel'].search([('code', '=', ac)])
                if not ac_id:
                    errors.append({'line_no': index, 'details': 'AC [{0}]  has invalid value'.format(ac)})

                sc = self.preprocess(rec['SC'])
                sc_id = self.env['servicing.channel'].search([('code', '=', sc)])
                if not sc_id:
                    errors.append({'line_no': index, 'details': 'SC [{0}]  has invalid value'.format(sc)})

                branch = self.preprocess(rec['BRANCH'])
                branch_id = self.env['operating.unit'].search([('code', '=', branch)])
                if not branch_id:
                    errors.append({'line_no': index, 'details': 'BRANCH  [{0}] has invalid value'.format(branch)})

                cost_centre = self.preprocess(rec['COST_CENTRE'])
                cost_centre_id = self.env['account.analytic.account'].search([('name', '=', cost_centre)])
                if not cost_centre_id:
                    errors.append(
                        {'line_no': index, 'details': 'COST_CENTRE [{0}]  has invalid value'.format(cost_centre)})

                if rec['COMP_1'] and rec['COMP_2']:
                    comp_1 = self.preprocess(rec['COMP_1'])
                    comp_2 = self.preprocess(rec['COMP_2'])

                    account = comp_1 + comp_2
                    account_id = self.env['account.account'].search([('code', '=', account)])
                    if not account_id:
                        errors.append({'line_no': index,
                                       'details': 'Combination of COMP_1 and COMP_2 has invalid value'.format(account)})

                if rec['DEBIT_CREDIT_FLAG'] == 'CR':
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

                if rec['DEBIT_CREDIT_FLAG'] == 'DR':
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
                moves[trn_no]['line_ids'].append((0, 0, line))

            if len(errors) > 0:
                self.env['server.file.error'].create({'file_path': source_path,
                                                      'errors': json.dumps(errors),
                                                      'ftp_ip': self.source_sftp_host})
            else:
                try:
                    for key in moves:
                        move_obj = self.env['account.move'].create(moves[key])
                        if move_obj.state == 'draft':
                            move_obj.post()
                    response = True
                except Exception:
                    self.env['server.file.error'].create(
                        {'file_path': dest_path, 'errors': 'Unknown Error. Please check your file.'})

        return response

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
