from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection(selection_add=[('lc', 'LC')],
                            help="Select 'LC' for LC operations journals.")