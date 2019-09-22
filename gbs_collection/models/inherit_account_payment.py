from odoo import api, fields, models, _


class InheritAccountPayment(models.Model):
    # _inherit = 'account.payment'
    _name = 'account.payment'
    _inherit = ['account.payment', 'mail.thread']

    sale_order_id = fields.Many2many('sale.order', string='Sale Order',
                                    readonly=True,
                                    states={'draft': [('readonly', False)]})
    is_this_payment_checked = fields.Boolean(string='Is This Payment checked with SO', default=False)
    my_menu_check = fields.Boolean(string='Check')
    is_cash_payment = fields.Boolean(string='Cash Payment', default=True)

    ## if cash
    deposited_bank = fields.Many2one('res.bank',string='Deposited Bank', readonly=True, states={'draft': [('readonly', False)]})
    bank_branch = fields.Char(string='Branch', readonly=True,states={'draft': [('readonly', False)]})
    deposit_slip = fields.Char(string='Deposit Slip No.',readonly=True,states={'draft': [('readonly', False)]})

    # if Bank
    cheque_no = fields.Char(string='Cheque No',readonly=True,states={'draft': [('readonly', False)]})
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
        ('transfer', 'Internal Transfer')
    ], string='Payment Type', default='inbound')

    payment_transaction_id = fields.Many2one('payment.transaction', string="Payment Transaction",readonly=True,states={'draft': [('readonly', False)]})

    is_entry_receivable_cleared_payments = fields.Boolean(string='Is this payments cleared receivable?')

    # for log
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')], track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='always')
    amount = fields.Monetary(string='Payment Amount', required=True, track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, track_visibility='onchange')
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))], track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False, string="Status", track_visibility='onchange')

    @api.multi
    def post(self):
        res = super(InheritAccountPayment, self).post()
        for s_id in self.sale_order_id:
            so_objs = self.env['sale.order'].search([('id', '=', s_id.id)])

            for so_id in so_objs:
                so_id.write({'is_this_so_payment_check': True})

        return res

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        res = super(InheritAccountPayment, self)._onchange_partner_type()
        if self.partner_type:
            return {'domain': {'partner_id': [(self.partner_type, '=', True),('parent_id', '=', False)]}}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            so_ids = set()
            if rec.partner_id:
                invoice_ids = self.env['account.invoice'].sudo().search([('partner_id', '=', rec.partner_id.id),
                                                                        ('state', '=', 'open'), ('so_id', '!=', False),
                                                                        ('sale_type_id.sale_order_type', 'in', ['cash', 'credit_sales'])])
                for inv in invoice_ids:
                    so_ids.add(inv.so_id.id)

                return {'domain': {'sale_order_id': [('id', 'in', list(so_ids))]}}
