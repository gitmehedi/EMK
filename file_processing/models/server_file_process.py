# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

import os
import shutil
import traceback
from contextlib import contextmanager
from datetime import datetime, timedelta
from glob import iglob
from odoo import exceptions, models, fields, api, _, tools
from odoo.service import db
import logging

_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')


class ServerFileProcess(models.Model):
    _name = 'server.file.process'
    _inherit = "mail.thread"

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Cannot duplicate a configuration."),
        ("days_to_keep_positive", "CHECK(days_to_keep >= 0)",
         "I cannot remove backups from the future. Ask Doc for that."),
    ]

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    folder = fields.Char(default=lambda self: self._default_folder(), required=True, string="Local Path Location")
    days_to_keep = fields.Integer(required=True, default=0, )
    method = fields.Selection(selection=[("local", "Local disk"), ("sftp", "Remote SFTP server")], default="local")

    source_sftp_host = fields.Char(string='SFTP Server')
    source_sftp_port = fields.Integer(string="SFTP Port", default=22)
    source_sftp_user = fields.Char(string='Username')
    source_sftp_password = fields.Char(string="SFTP Password")
    source_sftp_private_key = fields.Char(string="Primary Key Location")
    source_path = fields.Char(string="Path Location")

    dest_sftp_host = fields.Char(string='SFTP Server')
    dest_sftp_port = fields.Integer(string="SFTP Port", default=22)
    dest_sftp_user = fields.Char(string='Username')
    dest_sftp_password = fields.Char(string="SFTP Password")
    dest_sftp_private_key = fields.Char(string="PK Location")
    dest_path = fields.Char(string="Path Location")

    @api.model
    def _default_folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(
            tools.config["data_dir"],
            "backups",
            self.env.cr.dbname)

    @api.multi
    @api.depends("folder", "method", "source_sftp_host", "source_sftp_port", "source_sftp_user")
    def _compute_name(self):
        """Get the right summary for this job."""
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
        try:
            # Just open and close the connection
            with self.sftp_connection():
                raise exceptions.Warning(_("Connection Test Succeeded!"))
        except (pysftp.CredentialException,
                pysftp.ConnectionException,
                pysftp.SSHException):
            _logger.info("Connection Test Failed!", exc_info=True)
            raise exceptions.Warning(_("Connection Test Failed!"))

    @api.multi
    def action_backup(self):
        """Run selected backups."""
        backup = None
        filename = self.filename(datetime.now())
        successful = self.browse()

        # Start with local storage
        for rec in self.filtered(lambda r: r.method == "local"):
            with rec.backup_log():
                # Directory must exist
                try:
                    os.makedirs(rec.folder)
                except OSError:
                    pass

                with open(os.path.join(rec.folder, filename),
                          'wb') as destiny:
                    # Copy the cached backup
                    if backup:
                        with open(backup) as cached:
                            shutil.copyfileobj(cached, destiny)
                    # Generate new backup
                    else:
                        db.dump_db(self.env.cr.dbname, destiny)
                        backup = backup or destiny.name
                successful |= rec

        # Ensure a local backup exists if we are going to write it remotely
        sftp = self.filtered(lambda r: r.method == "sftp")
        if sftp:
            if backup:
                cached = open(backup)
            else:
                cached = db.dump_db(self.env.cr.dbname, None)

            with cached:
                for rec in sftp:
                    with rec.backup_log():
                        with rec.sftp_connection() as remote:
                            # Directory must exist
                            try:
                                remote.makedirs(rec.folder)
                            except pysftp.ConnectionException:
                                pass

                            # Copy cached backup to remote server
                            with remote.open(
                                    os.path.join(rec.folder, filename),
                                    "wb") as destiny:
                                shutil.copyfileobj(cached, destiny)
                        successful |= rec

        # Remove old files for successful backups
        successful.cleanup()

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
    def cleanup(self):
        """Clean up old backups."""
        now = datetime.now()
        for rec in self.filtered("days_to_keep"):
            with rec.cleanup_log():
                oldest = self.filename(now - timedelta(days=rec.days_to_keep))

                if rec.method == "local":
                    for name in iglob(os.path.join(rec.folder,
                                                   "*.dump.zip")):
                        if os.path.basename(name) < oldest:
                            os.unlink(name)

                elif rec.method == "sftp":
                    with rec.sftp_connection() as remote:
                        for name in remote.listdir(rec.folder):
                            if (name.endswith(".dump.zip") and
                                    os.path.basename(name) < oldest):
                                remote.unlink('%s/%s' % (rec.folder, name))

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

    @api.model
    def filename(self, when):
        """Generate a file name for a backup.

        :param datetime.datetime when:
            Use this datetime instead of :meth:`datetime.datetime.now`.
        """
        return "{:%Y_%m_%d_%H_%M_%S}.dump.zip".format(when)

    @api.multi
    def sftp_connection(self):
        """Return a new SFTP connection with found parameters."""
        self.ensure_one()
        if self.env.context.get('target') == 'source':
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
