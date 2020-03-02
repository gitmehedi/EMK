from odoo import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection(selection_add=[('situation', 'Opening/Closing Situation')],
                            help="Select 'Opening/Closing Situation' for Opening/Closing Journal journals.")
