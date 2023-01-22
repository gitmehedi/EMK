from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection(selection_add=[('provisional', 'Provisional')],
                            help="Select 'Provisional' for Provisional Expense operations journals.")