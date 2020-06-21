from odoo import api, fields, models, _, SUPERUSER_ID


class SecurityDepositReturn(models.Model):
    _name = "security.deposit.return"
    _description = 'Security Deposit Return'
    _order = 'name desc'
    _inherit = ['mail.thread']

    name = fields.Char(required=False, track_visibility='onchange', string='SDR No')
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='restrict', required=True,
                                 track_visibility='onchange', readonly=True,
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)],
                                 states={'draft': [('readonly', False)]})
    agreement_ids = fields.Many2many('agreement', 'agreement_security_return_rel', 'sd_return_id', 'agreement_id',
                                     required=True,string='Advances',
                                     readonly=True, states={'draft': [('readonly', False)]})
    total_amount = fields.Float(string="Amount", readonly=True,
                                track_visibility='onchange', states={'draft': [('readonly', False)]},
                                help="Total amount to be returned to vendor for security deposit purpose")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('done', "Done"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')