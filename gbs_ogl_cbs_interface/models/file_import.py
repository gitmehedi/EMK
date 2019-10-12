import os, shutil, base64, traceback, logging, json

from random import randint
from odoo import api, models, fields, _
from datetime import datetime


class GBSFileImport(models.Model):
    _name = 'gbs.file.import'
    _inherit = ['mail.thread']
    _description = "Import File"

    name = fields.Char(string='Title', required=True, track_visibility='onchange')
    date = fields.Datetime(string='Date', default=fields.Datetime.now, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed')], default='draft', string='State')
    import_lines = fields.One2many('gbs.file.import.line', 'import_id')

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Cannot duplicate the name !')
    ]

    @api.multi
    def action_process(self):
        record_date = datetime.strftime(datetime.now(), "%d%m%Y_%H%M%S_")
        process_date = datetime.strftime(datetime.now(), "%d%m%Y_")
        unique = str(randint(100, 999))
        filename = "MDC_41101_" + record_date + process_date + unique + ".txt"

        def generate_file(record):
            file_path = os.path.join(record.source_path, filename)
            with open(file_path, "w+") as file:
                for val in self.import_lines:
                    trn_type = val.type
                    account_no = str(val.account_no)
                    amount = format(val.amount, '.3f') if val.amount > 0 else format(val.amount, '.3f')
                    narration = val.narration[:50]
                    trn_ref_no = val.reference_no[-8:]
                    date_array = val.date.split("-")
                    date = date_array[2] + date_array[1] + date_array[0]

                    record = "{:2s}{:17s}{:16s}{:50s}{:8s}{:8s}\r\n".format(trn_type, account_no, amount, narration,
                                                                            trn_ref_no, date)
                    file.write(record)
                    val.write({'state': 'done'})
                self.write({'state': 'processed'})

            if os.stat(file_path).st_size == 0:
                os.remove(file_path)
            return True if os.path.exists(file_path) else False

        for rec in self.env['generate.cbs.journal'].search([('method', '=', 'sftp')]):
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
                                                                                   'file_name': filename})
                        if success:
                            os.remove(local_path)
                        else:
                            continue
                    else:
                        continue

    @api.one
    def directory_check(self, dirs):
        for dir in dirs:
            if not os.path.isdir(dir):
                try:
                    os.makedirs(dir)
                except OSError:
                    pass


class GBSFileImportLine(models.Model):
    _name = 'gbs.file.import.line'

    name = fields.Char(string='Name')
    account_no = fields.Char(string='Account No')
    amount = fields.Float(string='Amount')
    narration = fields.Char(string='Narration')
    reference_no = fields.Char(string='Reference No')
    date = fields.Char(string='Value Date')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', string='Status')
    type = fields.Selection([
        ('01', 'Credit Dep'),
        ('51', 'Debit Dep'),
        ('02', 'Backdated Credit Dep'),
        ('52', 'Backdated Debit Dep'),
        ('03', 'Credit Loan'),
        ('53', 'Debit Loan'),
        ('04', 'Credit Gen'),
        ('54', 'Debit Gen'),

    ], string='Type')

    import_id = fields.Many2one('gbs.file.import', 'Import Id', ondelete='cascade')
