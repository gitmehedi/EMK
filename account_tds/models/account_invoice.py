from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_applicable = fields.Boolean(string='Applicable',default=True,
        help="""TDS applicable/not applicable for this bill.
        If its not applicable then need to take dicission 
        that its for permanent or temporary.""")
    inapplicable_type = fields.Selection([
        ('temporary_inapplicable', 'Temporary'),
        ('permanent_inapplicable', 'Permanent')], string='Select Type',
        help="""If TDS not apply for this bill or supplier already give the TDS for this bill then it will permanently inapplicable.
        If there any chance to add TDS in this bill then its temporary inapplicable""")
