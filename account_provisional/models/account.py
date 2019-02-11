from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
        ('provisional', 'Provisional'),
    ], required=True,
        help="Select 'Sale' for customer invoices journals.\n" \
             "Select 'Purchase' for vendor bills journals.\n" \
             "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n" \
             "Select 'General' for miscellaneous operations journals.\n" \
             "Select 'Provisional' for Provisional Expense operations journals.")