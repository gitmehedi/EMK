from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorSecurityDeposit(models.Model):
    _name = 'vendor.security.deposit'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Vendor Security Deposit'

    name = fields.Char(required=True, track_visibility='onchange', string='Deposit Name', default='/', copy=False)
    active = fields.Boolean(strring='active', track_visibility='onchange', default=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='restrict', required=True,
                                 track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]},
                                 domain=[('supplier', '=', True)])
    account_id = fields.Many2one('account.account', string='Account', required=True, track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 domain=[('reconcile', '=', True)])
    amount = fields.Float(string="Amount", readonly=True,
                          track_visibility='onchange', states={'draft': [('readonly', False)]},
                          help="amount to be deposited to vendor for security deposit purpose")
    adjusted_amount = fields.Float(string="Adjusted Amount", readonly=True, default=0,
                                   track_visibility='onchange', copy=False)
    return_line_ids = fields.One2many('vendor.security.return.line', 'vsd_id',
                                      string='Security Return Lines', readonly=True)
    date = fields.Date(string='Date', track_visibility='onchange', copy=False)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('inactive', "Inactive"),
        ('done', "Closed")], default='draft', string="Status",
        track_visibility='onchange')
    maker_id = fields.Many2one('res.users', 'Maker', track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    outstanding_amount = fields.Float('Outstanding Amount', compute='_compute_outstanding_amount', readonly=True,
                                      help="Remaining Amount to adjustment.", store=True)
    description = fields.Char('Particulars', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})

    @api.depends('adjusted_amount', 'amount')
    def _compute_outstanding_amount(self):
        for rec in self:
            rec.outstanding_amount = rec.amount - rec.adjusted_amount

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                if not rec.amount > 0:
                    raise ValidationError(_("[Validation Error] Amount must be greater than Zero!"))
                sequence = self.env['ir.sequence'].next_by_code('vendor.security.deposit') or ''
                rec.write({
                    'state': 'confirm',
                    'name': sequence,
                    'maker_id': rec.env.user.id
                })

    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.state == 'confirm':
                if self.env.user.id == rec.maker_id.id and self.env.user.id != SUPERUSER_ID:
                    raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
                rec.write({
                    'state': 'approve',
                    'approver_id': self.env.user.id
                })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a security deposit which is not in draft mode!'))
        return super(VendorSecurityDeposit, self).unlink()
