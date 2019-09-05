from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


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

    def action_process(self):
        raise ValidationError(_('Work on process.'))



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