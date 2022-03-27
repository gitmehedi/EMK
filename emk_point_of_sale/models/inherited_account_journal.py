from odoo import models, fields, api,_
from odoo.exceptions import Warning


class InheritedAccountJournal(models.Model):
    _inherit = 'account.journal'
