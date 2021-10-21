from odoo import api, fields, models, _, sql_db
from odoo.service import db
import subprocess, os, base64
import logging

_logger = logging.getLogger(__name__)


class DBOperationManage(models.Model):
    _name = 'db.operation.manage'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Database Duplicate and Replication'
    _order = 'id desc'
    _rec_name = 'destination_db'

    name = fields.Char(string="Title", required=True, track_visibility='onchange')
    source_db = fields.Char(string='Source Database', required=True, track_visibility='onchange')
    source_ip = fields.Char(string='Source IP', track_visibility='onchange')
    source_port = fields.Char(string='Source Port', track_visibility='onchange')
    source_db_user = fields.Char(string='Source Username', track_visibility='onchange')
    source_db_pass = fields.Char(string='Source Password')
    destination_db = fields.Char(string='Dest. Database', required=True, track_visibility='onchange')
    dest_ip = fields.Char(string='Dest. IP', track_visibility='onchange')
    dest_port = fields.Char(string='Dest. IP', track_visibility='onchange')
    dest_db_user = fields.Char(string='Dest. Username', track_visibility='onchange')
    dest_db_pass = fields.Char(string='Dest. Password')
    backup_path = fields.Char(string="Backup Path", required=True)
    query = fields.Text(string="Generic Query", required=True)
    operation_type = fields.Selection([('duplicate', 'Duplicate'), ('restore', 'Restore'), ('backup', 'Backup')],
                                      required=True, track_visibility='onchange', string='Operation Type')
    location = fields.Selection([('local', 'Local'), ('remote', 'Remote')], default='local', required=True,
                                track_visibility='onchange', string='Location')
    line_ids = fields.One2many('db.operation.manage.line', 'line_id')

    @api.one
    def action_duplicate(self):
        if self.source_db and self.destination_db:
            drop_db = True
            if db.exp_db_exist(self.destination_db):
                drop_db = db.exp_drop(self.destination_db)

            create_db = db.exp_duplicate_database(self.source_db, self.destination_db)
            if create_db:
                with sql_db.db_connect(self.destination_db).cursor() as cr:
                    cr.execute("UPDATE ir_cron SET active=False")
                    cr.execute("UPDATE server_file_process SET status=False")
                    cr.execute("UPDATE soap_process SET status=False")
                    cr.execute("UPDATE auditlog_rule SET state='draft'")
                    cr.execute("UPDATE res_users SET active=False WHERE id !=1")

    @api.one
    def action_restore(self):
        if self.source_db and self.destination_db:
            filepath = os.path.join(self.backup_path, self.destination_db + ".tar")
            if os.path.isfile(filepath):
                os.system("rm -f {0}".format(filepath))

            src_cmd = "PGPASSWORD=\"{0}\" pg_dump -h {1} -p {2} -U {3}  -w -F t {4} > {5}".format(self.source_db_pass,
                                                                                                  self.source_ip,
                                                                                                  self.source_port,
                                                                                                  self.source_db_user,
                                                                                                  self.source_db,
                                                                                                  filepath)

            try:
                os.system(src_cmd)
            except OSError as e:
                _logger.info("Exception raise in backend", exc_info=True)

            if os.path.isfile(filepath):
                term_query = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=\'MTBL_REPORT\';"
                term_str = "PGPASSWORD=\"{0}\" psql -h {1} -p {2} -d {3} -c \"{4}\" -U {5} >/dev/null 2>&1".format(
                    self.dest_db_pass,
                    self.dest_ip,
                    self.dest_port,
                    'postgres',
                    term_query,
                    'postgres', )
                try:
                    os.system(term_str)
                except OSError as e:
                    _logger.info("Exception raise in terminate", exc_info=True)

                drop_query = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=\'MTBL_REPORT\';"
                drop_str = "PGPASSWORD=\"{0}\" psql -h {1} -p {2} -d {3} -c \"{4}\" -U {5} >/dev/null 2>&1".format(
                    self.dest_db_pass,
                    self.dest_ip,
                    self.dest_port,
                    self.destination_db,
                    drop_query,
                    self.dest_db_user)
                try:
                    os.system(drop_str)
                except OSError as e:
                    _logger.info("Exception raise in drop database", exc_info=True)

                dest_cmd = "PGPASSWORD=\"{0}\" pg_restore -h {1} -p {2} -d {3} -c {4} -U {5} -w >/dev/null 2>&1".format(
                    self.dest_db_pass,
                    self.dest_ip,
                    self.dest_port,
                    self.destination_db,
                    filepath,
                    self.dest_db_user)

                os.system(dest_cmd)
                try:
                    os.system(dest_cmd)
                except OSError as e:
                    _logger.info("Exception raise in restore", exc_info=True)

                try:
                    query_str = "PGPASSWORD=\"{0}\" psql -h {1} -p {2} -d {3} -c \"{4}\" -U {5}".format(
                        self.dest_db_pass,
                        self.dest_ip,
                        self.dest_port,
                        self.destination_db,
                        self.query,
                        self.dest_db_user)
                    output = subprocess.check_output(query_str, shell=True)
                    self.line_ids.create({
                        'name': "GLIF_DATE_{0}.txt".format(self.env.user.company_id.batch_date),
                        'date': self.env.user.company_id.batch_date,
                        'query_result': base64.b64encode(output),
                        'line_id': self.id,
                    })
                except OSError as e:
                    _logger.info("Exception raise in restore", exc_info=True)


class DBOperationManageLine(models.Model):
    _name = 'db.operation.manage.line'
    _rec_name = "name"
    _order = "id DESC"

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string='Date', required=True)
    query_result = fields.Binary(string="Result", attachment=True)
    line_id = fields.Many2one('db.operation.manage')
