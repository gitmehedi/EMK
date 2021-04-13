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
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))], track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False, string="Status", track_visibility='onchange')
    is_auto_invoice_paid = fields.Boolean(string='Auto Invoice Paid', track_visibility='onchange')

    @api.multi
    def post(self):
        # delete default_partner_type key from context
        if 'default_partner_type' in self.env.context:
            self.env.context = dict(self.env.context)
            del self.env.context['default_partner_type']

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
    def get_sale_order_ids(self):
        ids = []
        if self.partner_id.id:
            sql_str = """(SELECT
                            DISTINCT s.id
                        FROM
                            sale_order s
                            JOIN sale_order_type ot ON ot.id=s.type_id AND ot.sale_order_type='credit_sales'
                            JOIN account_invoice i ON i.origin=s.name AND i.state='open'
                        WHERE
                            s.partner_id=%s AND s.state='done')
                        UNION
                        (SELECT
                            DISTINCT s.id
                        FROM
                            sale_order s
                            JOIN sale_order_type ot ON ot.id=s.type_id AND ot.sale_order_type='cash'
                            LEFT JOIN account_invoice i ON i.so_id=s.id
                        WHERE
                            s.partner_id=%s AND s.state='done'
                            AND s.id NOT IN (SELECT s.id FROM account_invoice i 
                                             JOIN sale_order s ON s.name=i.origin 
                                             AND i.partner_id=%s AND i.state='paid'))    
            """
            self.env.cr.execute(sql_str, (self.partner_id.id, self.partner_id.id, self.partner_id.id))
            ids = self.env.cr.fetchall()

        return ids

    @api.onchange('narration')
    def onchange_narration(self):
        if self.narration:
            self.narration = self.narration.strip()

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        res = super(InheritAccountPayment, self)._onchange_partner_type()
        if self.partner_type:
            return {'domain': {'partner_id': [(self.partner_type, '=', True), ('parent_id', '=', False)]}}

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.sale_order_id = []
        ids = self.get_sale_order_ids()
        return {'domain': {'sale_order_id': [('id', 'in', ids)]}}

    @api.onchange('is_auto_invoice_paid')
    def onchange_is_auto_invoice_paid(self):
        self.sale_order_id = []
