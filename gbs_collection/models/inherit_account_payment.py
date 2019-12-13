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
    deposited_bank = fields.Many2one('res.bank',string='Customer Bank', readonly=True, states={'draft': [('readonly', False)]})
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
    partner_id = fields.Many2one('res.partner', string='Partner', track_visibility='always')
    amount = fields.Monetary(string='Payment Amount', required=True, track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, track_visibility='onchange')
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Collection Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))], track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False, string="Status", track_visibility='onchange')
    is_auto_invoice_paid = fields.Boolean(string='Auto Invoice Paid', track_visibility='onchange')

    @api.multi
    def post(self):
        if self.sale_order_id.ids or self.is_auto_invoice_paid:
            self.invoice_ids = self.get_invoice_ids()
        # post payment
        res = super(InheritAccountPayment, self).post()
        for s_id in self.sale_order_id:
            so_objs = self.env['sale.order'].search([('id', '=', s_id.id)])

            for so_id in so_objs:
                so_id.write({'is_this_so_payment_check': True})

        return res

    @api.multi
    def get_invoice_ids(self):
        if self.is_auto_invoice_paid:
            invoice_ids = self.env['account.invoice'].sudo().search([('partner_id', '=', self.partner_id.id),
                                                                     ('state', '=', 'open')])
        else:
            invoice_ids = self.env['account.invoice'].sudo().search([('so_id', 'in', self.sale_order_id.ids),
                                                                     ('state', '=', 'open')])
        return invoice_ids

    @api.multi
    def get_sale_order_id_list(self):
        so_ids = []
        if self.partner_id.id:
            sale_order_ids = self.env['sale.order'].sudo().search([('partner_id', '=', self.partner_id.id),
                                                                   ('state', '=', 'done'),
                                                                   ('type_id.sale_order_type', 'in',
                                                                    ['cash', 'credit_sales'])])
            for so in sale_order_ids:
                # check if so has any invoice in 'open' state.
                if len(self.env['account.invoice'].sudo().search([('so_id', '=', so.id), ('state', '=', 'open')])) > 0:
                    so_ids.append(so.id)
                # check if so type is 'cash' and has not created any invoice yet.
                elif so.type_id.sale_order_type == 'cash' and len(self.env['account.invoice'].sudo().search(
                        [('so_id', '=', so.id), ('state', '=', 'paid')])) <= 0:
                    so_ids.append(so.id)
                else:
                    pass

        return so_ids

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        res = super(InheritAccountPayment, self)._onchange_partner_type()
        if self.partner_type:
            return {'domain': {'partner_id': [(self.partner_type, '=', True), ('parent_id', '=', False)]}}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        id_list = self.get_sale_order_id_list()
        return {'domain': {'sale_order_id': [('id', 'in', id_list)]}}

    @api.onchange('is_auto_invoice_paid')
    def onchange_is_auto_invoice_paid(self):
        self.sale_order_id = []

    def _get_counterpart_move_line_vals(self, invoice=False):
        res = super(InheritAccountPayment, self)._get_counterpart_move_line_vals(self.invoice_ids)
        if self.is_auto_invoice_paid:
            name = res['name'].split(':')[0] + ': By Auto Paid'
            res['name'] = name
        elif self.sale_order_id.ids:
            name = res['name'].split(':')[0] + ': '
            for so in self.sale_order_id:
                name += so.name + ', '
            res['name'] = name[:len(name)-2]
        else:
            pass

        return res
