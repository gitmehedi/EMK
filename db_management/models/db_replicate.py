from odoo import api, fields, models, _, sql_db
from odoo.service import db


class DBDuplicate(models.Model):
    _name = 'db.replicate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Database Duplicate and Replication'
    _order = 'id desc'
    _rec_name = 'destination_db'

    source_db = fields.Char(string='Source Database', required=True, track_visibility='onchange')
    destination_db = fields.Char(string='Destination Database', required=True, track_visibility='onchange')
    operation_type = fields.Selection([('duplicate', 'Duplicate'), ('restore', 'Restore'), ('backup', 'Backup')],
                                      required=True, track_visibility='onchange')

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
