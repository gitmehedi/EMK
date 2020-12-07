from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class ChequeReceived(models.Model):
    _name = 'accounting.cheque.received'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id DESC'
    _description = "Cheque Info"

    state = fields.Selection([
        ('draft', 'Cheque Entry'),
        ('received', 'Confirm'),
        ('deposited', 'Deposit to Bank'),
        ('honoured', 'Honoured'),
        ('dishonoured', 'Dishonoured'),
        ('returned', 'Returned to Customer'),
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')], default='customer')
    payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True,
                                    default='inbound')
    invoice_ids = fields.Many2many('account.invoice', 'account_invoice_check_received_rel', 'cheque_received_id',
                                   'invoice_id', string="Invoices", copy=False, readonly=True)

    @api.multi
    def _get_name(self):
        for n in self:
            n.name = 'Customer Collection'

    name = fields.Char(string='Name', compute='_get_name')

    partner_id = fields.Many2one('res.partner', domain=[('active', '=', True), ('customer', '=', True)], string="Customer", required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    bank_name = fields.Many2one('res.bank', string='Bank', required=True,states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    branch_name = fields.Char(string='Branch Name', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    date_on_cheque = fields.Date('Date On Cheque', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    cheque_amount = fields.Float(string='Amount', required=True, states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    sale_order_id = fields.Many2many('sale.order', string='Sale Order',
                                     states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]}) #domain=[('partner_id', '=', partner_id.id),('is_this_so_payment_check','=',False),('state', '=', 'done')]

    partner_id = fields.Many2one('res.partner',
                                 domain=[('parent_id', '=', False), ('active', '=', True), ('customer', '=', True)],
                                 string="Customer", required=True,
                                 states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                         'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                         'deposited': [('readonly', True)]})
    bank_name = fields.Many2one('res.bank', string='Bank', required=True,
                                states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                        'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                        'deposited': [('readonly', True)]})
    branch_name = fields.Char(string='Branch Name', required=True,
                              states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                      'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                      'deposited': [('readonly', True)]})
    date_on_cheque = fields.Date('Date On Cheque', required=True,
                                 states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                         'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                         'deposited': [('readonly', True)]})
    cheque_amount = fields.Float(string='Amount', required=True,
                                 states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                         'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                         'deposited': [('readonly', True)]})

    is_cheque_payment = fields.Boolean(string='Cheque Payment', default=True)
    company_id = fields.Many2one('res.company', string='Company', ondelete='cascade',
                                 default=lambda self: self.env.user.company_id, readonly='True',
                                 states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                         'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                         'deposited': [('readonly', True)]})

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False,
                               states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                       'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                       'deposited': [('readonly', True)]})

    # @todo : Update this field
    is_this_payment_checked = fields.Boolean(string='is_this_payment_checked', default=False)
    cheque_no = fields.Char(string='Cheque No', states = {'returned': [('readonly', True)],'dishonoured': [('readonly', True)],'honoured': [('readonly', True)],'received': [('readonly', True)],'deposited': [('readonly', True)]})
    is_entry_receivable_cleared = fields.Boolean(string='Is this entry cleared receivable?')
    narration = fields.Text(string='Narration', states={'returned': [('readonly', True)],
                                                        'dishonoured': [('readonly', True)],
                                                        'honoured': [('readonly', True)],
                                                        'received': [('readonly', True)],
                                                        'deposited': [('readonly', True)]}, track_visibility='onchange')
    honoured_date = fields.Date(string='Honoured Date', readonly=True, track_visibility='onchange')

    @api.onchange('narration')
    def onchange_narration(self):
        if self.narration:
            self.narration = self.narration.strip()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.sale_order_id = []
        ids = self.get_sale_order_ids()
        return {'domain': {'sale_order_id': [('id', 'in', ids)]}}

    @api.multi
    def _get_payment_method(self):
        for pay in self:
            pay_method_pool = pay.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1)
            pay.payment_method_id = pay_method_pool.id

    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', )
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                          'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                          'deposited': [('readonly', True)]})

    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')],
                                    string='Payment Type', required=True, default='inbound')

    @api.onchange('partner_id')
    def _on_change_partner_id(self):
        for pay in self:
            pay_method_pool = pay.env['account.payment.method'].search([('payment_type', '=', 'inbound')], limit=1)
            pay.payment_method_id = pay_method_pool.id

    journal_id = fields.Many2one('account.journal', string='Payment Journal',
                                 states={'returned': [('readonly', True)], 'dishonoured': [('readonly', True)],
                                         'honoured': [('readonly', True)], 'received': [('readonly', True)],
                                         'deposited': [('readonly', True)]}, domain=[('type', '=', 'bank')])

    @api.constrains('currency_id')
    def _check_currency_with_companys_currency(self):
        if self.journal_id and self.currency_id:
            if self.journal_id.currency_id:
                if self.currency_id != self.journal_id.currency_id:
                    raise ValidationError('Payment Journal Currency and Cheque Received Currency must be same')
            else:
                if self.currency_id != self.journal_id.company_id.currency_id:
                    raise ValidationError('Payment Journal Currency and Cheque Received Currency must be same')

    @api.constrains('cheque_amount')
    def _check_negative_amount_value(self):
        if self.cheque_amount < 0:
            raise ValidationError('The payment amount must be strictly positive.')

        if self.cheque_amount == 0:
            raise ValidationError('The payment amount must be greater than zero')

    @api.multi
    def updateCustomersCreditLimit(self):
        # Update customer's Credit Limit. Basically plus cheque amount with Customer Credit Limit
        for cust in self:
            res_partner_credit_limit = cust.env['res.partner.credit.limit'].search(
                [('partner_id', '=', cust.partner_id.id),
                 ('state', '=', 'approve')], order='id DESC', limit=1)

            # Cheque Amount with Credit limit of customer; it should not exceed customer's original Credit Limit.
            if cust.sale_order_id.credit_sales_or_lc == 'credit_sales' \
                    and cust.sale_order_id.partner_id.id == cust.partner_id.id:

                update_cust_credits = res_partner_credit_limit.remaining_credit_limit + cust.cheque_amount

                if update_cust_credits > res_partner_credit_limit.value:
                    res_partner_credit_limit.write({'remaining_credit_limit': res_partner_credit_limit.value})
                else:
                    res_partner_credit_limit.write({'remaining_credit_limit': update_cust_credits})

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('accounting.cheque.received') or '/'
        vals['name'] = seq
        return super(ChequeReceived, self).create(vals)

    @api.multi
    def unlink(self):
        """ delete function """
        for rec in self:
            if rec.state == 'honoured':
                raise UserError(_("You can not delete a check received which is in honoured state."))
        return super(ChequeReceived, self).unlink()

    @api.multi
    def action_received(self):
        for cr in self:
            cr.state = 'received'

    @api.multi
    def action_deposited(self):
        for cr in self:
            if not cr.journal_id:
                wizard_form = self.env.ref('gbs_accounting_cheque_received.journal_adding_cheque_view', False)
                view_id = self.env['journal.adding.wizard']
                return {
                    'name': _('Payment Journal'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'journal.adding.wizard',
                    'res_id': view_id.id,
                    'view_id': wizard_form.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                   # 'context': {'delivery_order_id': self.id}
                }

            cr.state = 'deposited'

    @api.multi
    def action_dishonoured(self):
        for cr in self:
            cr.state = 'dishonoured'

    @api.multi
    def action_returned_to_customer(self):
        for cr in self:
            cr.state = 'returned'

    @api.multi
    def action_honoured(self):
        for rec in self:
            if not rec.honoured_date:
                ids = self.get_sale_order_ids()
                wizard = self.env.ref('gbs_accounting_cheque_received.add_honoured_date_wizard_view_form')
                return {
                    'name': _('Honoured Information'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'add.honoured.date.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': wizard.id,
                    'context': {'default_sale_order_ids': self.sale_order_id.ids, 'domain_ids': ids},
                    'target': 'new'
                }

            if rec.sale_order_id.ids:
                rec.invoice_ids = self.env['account.invoice'].sudo().search([('so_id', 'in', self.sale_order_id.ids),
                                                                             ('state', '=', 'open')])
            amount = rec.cheque_amount * (rec.payment_type == 'outbound' and 1 or -1)
            move = rec._create_journal_entry(amount)

            for s_id in rec.sale_order_id:
                so_objs = rec.env['sale.order'].search([('id', '=', s_id.id)])
                for so_id in so_objs:
                    so_id.write({'is_this_so_payment_check': True})

            rec.write({'state': 'honoured'})

    @api.multi
    def _create_journal_entry(self, amount):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)

        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the payment in that currency too
            invoice_currency = self.invoice_ids[0].currency_id

        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.date_on_cheque).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                            invoice_currency)

        move = self.env['account.move'].create({
            'date': self.honoured_date,
            'company_id': self.company_id.id,
            'journal_id': self.journal_id.id,
        })

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals())
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        self.invoice_ids.register_payment(counterpart_aml)

        # Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        # post account move
        move.post()

        return move

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = journal.with_context(ir_sequence_date=self.date_on_cheque).sequence_id.next_by_id()
        return {
            'name': name,
            'date': self.date_on_cheque,
            'company_id': self.company_id.id,
            'journal_id': journal.id,
        }

    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
        }

    def _get_counterpart_move_line_vals(self):
        name = ''
        if self.partner_type == 'customer':
            # name += _("Customer Payment By Check") if self.payment_type == 'inbound' else _("Customer Refund By Check")
            name = self.narration
        else:
            name += _("Vendor Refund By Check") if self.payment_type == 'inbound' else _("Vendor Payment By Check")

        # if self.sale_order_id.ids:
        #     name += ': '
        #     for so in self.sale_order_id:
        #         name += so.name + ', '
        #     name = name[:len(name)-2]

        if self.partner_id.id:
            destination_account_id = self.partner_id.property_account_receivable_id.id \
                if self.partner_type == 'customer' else self.partner_id.property_account_payable_id.id

        return {
            'name': name,
            'account_id': destination_account_id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'cheque_received_id': self.id,
        }

    def _get_liquidity_move_line_vals(self, amount):
        vals = {
            'name': self.name,
            'account_id': self.payment_type == 'outbound' and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'cheque_received_id': self.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('cheque_received_id', 'in', self.ids)],
        }

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
