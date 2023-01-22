from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread', 'ir.needaction_mixin']

    journal_id = fields.Many2one(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange', default=lambda self: self.env.user.company_id.batch_date)
    ref = fields.Char(states={'posted': [('readonly', True)]}, track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')
    narration = fields.Text(states={'posted': [('readonly', True)]}, track_visibility='onchange')
    partner_id = fields.Many2one(string='Vendor')
    operating_unit_id = fields.Many2one(string='Branch', track_visibility='onchange',
                                        states={'posted': [('readonly', True)]},
                                        default=lambda self: self.env.user.default_operating_unit_id)
    is_cbs = fields.Boolean(default=False, help='CBS data always sync with OGL using GLIF.')
    is_sync = fields.Boolean(default=False, copy=False, help='OGL continuously send data to CBS for journal sync.')
    is_cr = fields.Boolean(default=False)
    user_id = fields.Many2one('res.users', 'Maker')
    total_debit = fields.Char(compute='_compute_sum', string="Total Debit")
    total_credit = fields.Char(compute='_compute_sum', string="Total Credit")
    missmatch_value = fields.Char(compute='_compute_sum', string="Amount Variance")

    maker_id = fields.Many2one('res.users', 'Maker', track_visibility='onchange', copy=False)
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange', copy=False)

    @api.depends('line_ids')
    def _compute_sum(self):
        for rec in self:
            if rec.is_cbs:
                prec = self.env['decimal.precision'].precision_get('Account')
                self._cr.execute("""\
                                SELECT  SUM(debit) AS debit,
                                        SUM(credit) AS credit,
                                        sum(credit) - sum(debit) as missmatch
                                FROM account_move_line                 
                                WHERE move_id = %s
                                """ % rec.id)

                for val in self.env.cr.fetchall():
                    if not val[0] and not val[1] and not val[2]:
                        pass
                    else:
                        rec.total_debit = "{:.2f}".format(val[0])
                        rec.total_credit = "{:.2f}".format(val[1])
                        rec.missmatch_value = "{:.2f}".format(val[2])

    @api.multi
    def post(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        return super(AccountMove, self).post()

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('posted',)), ('is_sync', '=', False)]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    name = fields.Char(string="Narration")
    account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)])
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string="Sequence")
    segment_id = fields.Many2one('segment', string="Segment")
    acquiring_channel_id = fields.Many2one('acquiring.channel', string="AC")
    servicing_channel_id = fields.Many2one('servicing.channel', string="SC")
    operating_unit_id = fields.Many2one(string='Branch')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre')
    reconcile_ref = fields.Char(string="Reconciliation Ref#", size=20)
    tin = fields.Char(related='partner_id.tin', string="TIN")
    bin = fields.Char(related='partner_id.bin', string="BIN")
    bill_amount = fields.Monetary(related='invoice_id.amount_total', string="Bill Amount")
    vat_tax_rate = fields.Char(related='tax_line_id.name', string="VAT/TAX Rate")