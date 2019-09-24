import os, shutil, base64, traceback, logging
from random import randint
from odoo import api, models, fields, _
from datetime import datetime


_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')


class GBSFileImport(models.Model):
    _name = 'gbs.file.import'
    _inherit = ['mail.thread']

    name = fields.Char(string='Title', required=True,track_visibility='onchange')
    import_creation_date_time = fields.Datetime(string='Date',default=fields.Datetime.now,track_visibility='onchange')

    """ Relational fields"""
    import_lines = fields.One2many('gbs.file.import.line', 'import_id')

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Cannot duplicate the name !')
    ]

    @api.multi
    def action_process(self):
        record_date = datetime.strftime(datetime.now(), "%d%m%Y_%H%M%S_")
        process_date = datetime.strftime(datetime.now(), "%d%m%Y_")
        unique = str(randint(100, 999))
        filename = "File_" + record_date + process_date + unique + ".txt"
        current_path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(current_path[:-6]+'/file_folder'):
            os.makedirs(current_path[:-6]+'/file_folder')
            path = current_path[:-6]+'file_folder'
        else:
            path = current_path[:-6]+'file_folder'
        file_path = os.path.join(path, filename)
        records = self.import_lines.search([('import_id','=',self.id),('state', '=', 'imported')])
        with open(file_path, "w+") as file:
            for val in records:
                account_no = val.account_no or None
                amount = val.amount or None
                reference_no = val.reference_no or None
                value = val.value or None
                type = val.type or None
                date = val.date or None
                narration = val.narration or None

                record = "{0}|{1}|{2}|{3}|{4}|{5}|{6}\r\n".format(account_no, amount, narration,
                                                                  reference_no, date, value,type)
                file.write(record)
                val.write({'state': 'done'})

        file.close()
        if os.stat(file_path).st_size == 0:
            os.remove(file_path)
        return True if os.path.exists(file_path) else False



class GBSFileImportLine(models.Model):
    _name = 'gbs.file.import.line'

    name = fields.Char(string='Name')
    account_no = fields.Char(string='Account No')
    amount = fields.Char(string='Amount')
    narration = fields.Char(string='Narration')
    reference_no = fields.Char(string='Reference No')
    value = fields.Char(string='Value')
    date = fields.Char(string='Date')
    state = fields.Char(string='Status')
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