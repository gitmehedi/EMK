# -*- coding: utf-8 -*-

import os, shutil, base64, traceback, logging, json, re
from datetime import datetime
from contextlib import contextmanager
from odoo import exceptions, models, fields, api, _, tools
from odoo.exceptions import ValidationError
from random import randint

_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class GenerateCBSJournal(models.Model):
    _name = 'generate.cbs.journal'
    _description = "CBS Batch Process"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'

    name = fields.Char(string="Name", required=True, track_visibility='onchange')
    folder = fields.Char(default=lambda self: self._default_path(), string="Local Folder Path",
                         track_visibility='onchange')
    days_to_keep = fields.Integer(required=True, default=0, )
    method = fields.Selection(selection=[("local", "Local Location"), ("sftp", "Middleware Location")], default="sftp",
                              required=True, track_visibility='onchange')

    source_path = fields.Char(string="Source Path", required=True, track_visibility='onchange')
    source_sftp_host = fields.Char(string='SFTP Server', track_visibility='onchange')
    source_sftp_port = fields.Integer(string="SFTP Port", default=22, track_visibility='onchange')
    source_sftp_user = fields.Char(string='Username', track_visibility='onchange')
    source_sftp_password = fields.Char(string="SFTP Password")
    source_sftp_private_key = fields.Char(string="Primary Key Location", track_visibility='onchange')

    dest_path = fields.Char(string="Destination Path", required=True, track_visibility='onchange')
    dest_sftp_host = fields.Char(string='SFTP Server', track_visibility='onchange')
    dest_sftp_port = fields.Integer(string="SFTP Port", default=22, track_visibility='onchange')
    dest_sftp_user = fields.Char(string='Username', track_visibility='onchange')
    dest_sftp_password = fields.Char(string="SFTP Password")
    dest_sftp_private_key = fields.Char(string="Primary Key Location", track_visibility='onchange')
    status = fields.Boolean(default=True, string='Status')

    @api.constrains('source_path', 'dest_path', 'folder')
    def onchange_path(self):
        if self.source_path:
            if not os.path.exists(self.source_path):
                raise ValidationError(_('Source Path [{0}] doesn\'t exists.'.format(self.source_path)))

        if self.method == 'local':
            if self.dest_path:
                if not os.path.exists(self.dest_path):
                    raise ValidationError(_('Destination Path [{0}] doesn\'t exists.'.format(self.dest_path)))

        if self.method == 'sftp':
            with self.sftp_connection('destination') as destination:
                if self.dest_path:
                    if not destination.exists(self.dest_path):
                        raise ValidationError(_('Destination Path [{0}] doesn\'t exists.'.format(self.dest_path)))

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
        try:
            conn = pysftp.Connection(**params)
        except Exception as e:
            raise ValidationError(_("Operation Error: %s".format(e)))

        return conn

    @api.multi
    def generate_journal(self):
        filename = self.generate_filename()

        def generate_file(record):
            move_ids = []
            file_path = os.path.join(record.source_path, filename)
            journals = self.env['account.move'].search(
                [('is_cbs', '=', False), ('is_sync', '=', False), ('is_opening', '=', False),('state', '=', 'posted')])
            with open(file_path, "w+") as file:
                for vals in journals:
                    for val in vals.line_ids:
                        trn_type = '54' if val.debit > 0 else '04'
                        amount = format(val.debit, '.2f') if val.debit > 0 else format(val.credit, '.2f')
                        amount = ''.join(amount.split('.')).zfill(16)
                        narration = re.sub(r'[|\n||\r|?|$|.|!]', r' ', val.name[:50])
                        trn_ref_no = ''.join(vals.name.split('/'))[-8:]
                        date_array = val.date.split("-")
                        date = date_array[2] + date_array[1] + date_array[0]
                        cost_centre = str(
                            "0" + val.analytic_account_id.code) if val.analytic_account_id.code else '0000'
                        account_no = str(val.account_id.code)
                        sub_opu = str(val.sub_operating_unit_id.code) if val.sub_operating_unit_id.code else '001'
                        branch_code = str("00" + val.operating_unit_id.code) if val.operating_unit_id.code else '00001'
                        bgl = "0{0}{1}{2}".format(account_no, sub_opu, branch_code)

                        journal = "{:2s}{:17s}{:16s}{:50s}{:8s}{:8s}{:4s}\r\n".format(trn_type, bgl, amount, narration,
                                                                                      trn_ref_no, date, cost_centre)
                        file.write(journal)

                    move_ids.append((0, 0, {'move_id': vals.id}))
                    vals.write({'is_sync': True})

            if os.stat(file_path).st_size == 0:
                os.remove(file_path)
            return move_ids if os.path.exists(file_path) else False

        record = self.env['server.file.process'].search([('method', '=', 'dest_sftp'),
                                                         ('type', '=', 'batch'),
                                                         ('status', '=', True)], limit=1)
        for rec in record:
            with rec.sftp_connection('destination') as destination:
                dirs = [rec.folder, rec.source_path, rec.dest_path]
                self.directory_check(dirs)
                start_date = fields.Datetime.now()
                file = generate_file(rec)

                dest_path = os.path.join(rec.dest_path, filename)
                local_path = os.path.join(rec.source_path, filename)

                if file:
                    if destination.put(local_path, dest_path):
                        with open(local_path, "rb") as cbs_file:
                            encoded_file = base64.b64encode(cbs_file.read())
                        stop_date = fields.Datetime.now()
                        success = self.env['generate.cbs.journal.success'].create({'name': filename,
                                                                                   'start_date': start_date,
                                                                                   'stop_date': stop_date,
                                                                                   'upload_file': encoded_file,
                                                                                   'file_name': filename,
                                                                                   'line_ids': file,
                                                                                   })
                        if success:
                            os.remove(local_path)
                        else:
                            continue
                    else:
                        continue

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

    @api.multi
    def strslice(self, pattern, lists):
        first, last = 0, 0
        values = []
        for val in lists:
            last += val
            values.append(pattern[first:last])
            first += val
        return values

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
                    "gbs_ogl_cbs_interface.mail_message_subtype_failure"
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
                subtype=self.env.ref("gbs_ogl_cbs_interface.failure"))
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

    def generate_filename(self):
        rec_date = self.env.user.company_id.batch_date.split('-')
        record_date = "{0}{1}{2}_".format(rec_date[2], rec_date[1], rec_date[0]) + datetime.strftime(datetime.now(),
                                                                                                     "%H%M%S_")
        process_date = "{0}{1}{2}_".format(rec_date[2], rec_date[1], rec_date[0])
        unique = str(randint(100, 999))
        return "MDC_00001_" + record_date + process_date + unique + ".txt"


