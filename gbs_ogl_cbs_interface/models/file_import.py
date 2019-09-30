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
                    account_no = val.account_no or None
                    amount = val.amount or None
                    reference_no = val.reference_no or None
                    value = val.value or None
                    type = val.type or None
                    date = val.date or None
                    narration = val.narration or None
                    record = "{0}|{1}|{2}|{3}|{4}|{5}|{6}\r\n".format(account_no, amount, narration,
                                                                      reference_no, date, value, type)
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
                        os.remove(local_path)
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
    value = fields.Float(string='Value')
    date = fields.Char(string='Date')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', string='Status')
    type = fields.Selection([
        ('credit_dep', 'Credit Dep'),
        ('debit_dep', 'Debit Dep'),
        ('backdated_credit', 'Backdated Credit Dep'),
        ('backdated_debit', 'Backdated Debit Dep'),
        ('credit_loan', 'Credit Loan'),
        ('debit_loan', 'Debit Loan'),
        ('credit_gen', 'Credit Gen'),
        ('debit_gen', 'Debit Gen'),

    ], string='Type')

    import_id = fields.Many2one('gbs.file.import', 'Import Id', ondelete='cascade')
