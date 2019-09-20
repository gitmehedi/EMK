from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class LCReceivablePayment(models.Model):

    _name = 'lc.receivable.payment'
    _description = 'LC Receivable Payment'
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "date desc"

    name = fields.Char(string='Reference', readonly=True, index=True,default='Draft',
                       track_visibility='onchange')
    lc_id = fields.Many2one('letter.credit', 'LC', ondelete='cascade',required=True,
                            readonly=True,states={'draft': [('readonly', False)]},
                            domain=[('type', '=', 'export')],
                            track_visibility = 'onchange')
    shipment_id = fields.Many2one('purchase.shipment','Shipment', ondelete='cascade',required=True,
                                  readonly=True, states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency',readonly=True,store=True,
                                  track_visibility='onchange',compute='_compute_rate_amounts')
    invoice_amount = fields.Float(string='Invoice Amount',readonly=True,store=True,
                                  track_visibility='onchange',compute='_compute_rate_amounts')
    currency_rate = fields.Float(string='Currency Rate',readonly=True,store=True,
                                 track_visibility='onchange',compute='_compute_rate_amounts')
    amount_in_company_currency = fields.Float(string='Base Amount',readonly=True,store=True,
                                              track_visibility='onchange',compute='_compute_rate_amounts')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre', ondelete="cascade",
                                          readonly=True, states={'draft': [('readonly', False)]},
                                          track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',readonly=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    date = fields.Datetime('Date', index=True, default=fields.Datetime.now,
                           readonly=True,states={'draft': [('readonly', False)]},
                           track_visibility = 'onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Posted'),
                              ('cancel', 'Cancelled')], string='Status', default='draft',
                             track_visibility='onchange')
    invoice_ids = fields.Many2many('account.invoice',
                                   'lc_collection_invoice_rel',
                                   'lc_collection_id',
                                   'invoice_id',
                                   'Invoices',readonly=True,required=True,
                                   states={'draft': [('readonly', False)]})
    currency_loss_gain_amount = fields.Float(string='Loss/Gain Amount',compute='_compute_currency_loss_gain',
                                             track_visibility='onchange')
    currency_loss_gain_type = fields.Selection([('margin', 'Margin'),
                                                ('loss', 'Loss'),
                                                ('gain', 'Gain'),], string='Loss/Gain Type', default='margin',
                                               compute='_compute_currency_loss_gain',
                                               track_visibility='onchange')
    particular = fields.Char(string='Particular', readonly=True, states={'draft': [('readonly', False)]},
                             track_visibility='onchange')
    analytic_acc_create = fields.Boolean('Need to create Analytic Account',default=False)
    journal_id = fields.Many2one('account.journal', string='Account Journal', ondelete="cascade",
                                 domain=[('type', '=', 'lc')],required=True,readonly=True,
                                 states={'draft': [('readonly', False)]},track_visibility='onchange')
    reference = fields.Text(string='Reference', compute='_compute_reference', readonly=True, store=False)

    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True,copy=False)
    """ Relational Fields """
    lc_receivable_collection_ids = fields.One2many('lc.receivable.collection', 'collection_parent_id',
                                                   string="Collections",readonly=True,
                                                   states={'draft': [('readonly', False)]})
    lc_receivable_charges_ids = fields.One2many('lc.receivable.charges', 'charges_parent_id',
                                                string="Charges",readonly=True,
                                                states={'draft': [('readonly', False)]})

    @api.onchange('lc_id')
    def onchange_lc_id(self):
        if self.lc_id:
            self.shipment_id = []
            self.invoice_ids = []
            self.currency_id = []
            self.invoice_amount = []
            self.amount_in_company_currency = []
            self.lc_receivable_collection_ids = []
            self.lc_receivable_charges_ids = []
            self.analytic_account_id = False
            self.analytic_acc_create = False
            invoice_ids = []
            shipment_ids = []
            shipment_objs = self.env['purchase.shipment'].search([('lc_id', '=', self.lc_id.id)])
            if shipment_objs:
                shipment_ids = shipment_objs.ids

            if self.lc_id.pi_ids_temp:
                so_objs = self.env['sale.order'].search([('pi_id', 'in',self.lc_id.pi_ids_temp.ids)])
                if so_objs:
                    for so_obj in so_objs:
                        for invoice_id in so_obj.invoice_ids:
                            invoice_ids.append(invoice_id.id)
            analytic_account_id = False
            if self.lc_id.analytic_account_id:
                analytic_account_id = self.lc_id.analytic_account_id.id
                self.analytic_account_id = analytic_account_id
            else:
                self.analytic_acc_create = True
            return {
                'domain': {'shipment_id': [('id', 'in', shipment_ids)],
                           'invoice_ids': [('id', 'in', invoice_ids),
                                           ('currency_id','=',self.lc_id.currency_id.id),
                                           ('state','=','open')],
                           'analytic_account_id': [('id', '=', analytic_account_id)]
                           }
            }

    @api.multi
    @api.depends('lc_id', 'date', 'invoice_ids')
    def _compute_rate_amounts(self):
        for record in self:
            if record.lc_id and record.invoice_ids:
                record.currency_id = record.lc_id.currency_id.id
                record.invoice_amount = sum(rec.residual for rec in record.invoice_ids)
                record.currency_rate = record.invoice_ids[0].conversion_rate
                record.amount_in_company_currency = sum(rec.residual*rec.conversion_rate for rec in record.invoice_ids)

    @api.multi
    @api.depends('lc_receivable_collection_ids.amount_in_company_currency',
                 'lc_receivable_charges_ids.amount_in_company_currency')
    def _compute_currency_loss_gain(self):
        for rec in self:
            total_collection_amount = 0.0
            total_charges_amount = 0.0
            if rec.lc_receivable_collection_ids:
                total_collection_amount = sum(line.amount_in_company_currency for line in rec.lc_receivable_collection_ids)
            if rec.lc_receivable_charges_ids:
                total_charges_amount = sum(line.amount_in_company_currency for line in rec.lc_receivable_charges_ids)

            rec.currency_loss_gain_amount = rec.amount_in_company_currency - (total_collection_amount + total_charges_amount)
            if rec.currency_loss_gain_amount >= rec.amount_in_company_currency:
                rec.currency_loss_gain_amount = 0.0
            if rec.currency_loss_gain_amount < 0:
                rec.currency_loss_gain_type = 'loss'
            elif rec.currency_loss_gain_amount > 0:
                rec.currency_loss_gain_type = 'gain'
            else:
                rec.currency_loss_gain_type = 'margin'

    @api.depends('shipment_id')
    def _compute_reference(self):
        for res in self:
            if res.shipment_id:
                res.reference = res.shipment_id.comment

    @api.multi
    def action_confirm(self):
        if not self.analytic_account_id:
            raise UserError(_('Without Analytic Account can not be confirmed!'))
        if self.name == 'Draft':
            new_seq = self.env['ir.sequence'].next_by_code('lc.collection.sequence')
            self.name = new_seq
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        account_move_obj = self.env['account.move']
        # account_move_line_obj = self.env['account.move.line']
        acc_move_line_list = []
        for collection_line in self.lc_receivable_collection_ids:
            acc_move_line_list.append(collection_line)
        for charge_line in self.lc_receivable_charges_ids:
            acc_move_line_list.append(charge_line)
        move_obj = False
        if acc_move_line_list:
            move_obj = self._generate_move(account_move_obj,self.journal_id)
            account_move_id = move_obj.id
            credit_amount = sum(i.amount_in_company_currency for i in acc_move_line_list)
            amount_currency = \
                sum(i.amount_in_currency if i.currency_id == self.currency_id
                    else i.amount_in_currency*self.currency_id.rate for i in acc_move_line_list)
            move_line_vals = []
            account_id = self.invoice_ids[0].account_id.id
            name = "Customer Payment"
            credit_move_obj = self._generate_credit_move_line(account_move_id,account_id,credit_amount,amount_currency,name)
            move_line_vals.append(credit_move_obj)
            for line in acc_move_line_list:
                debit_move_obj = self._generate_debit_move_line(account_move_id,line)
                move_line_vals.append(debit_move_obj)
            move_obj.line_ids = move_line_vals
            move_obj.post()
            self.lc_pay_and_reconcile(self.journal_id,move_obj,credit_amount)

        # exchange_amount = self.amount_in_company_currency - (credit_amount+self.currency_loss_gain_amount)
        if self.currency_loss_gain_type != 'margin':
            exchange_move_obj = self._generate_move(account_move_obj, self.company_id.currency_exchange_journal_id)
            exchange_account_move_id = exchange_move_obj.id
            move_line_vals = []
            if self.currency_loss_gain_type == 'gain':
                credit_amount = self.currency_loss_gain_amount
                amount_currency = self.currency_loss_gain_amount*self.currency_id.rate
                account_id = self.company_id.currency_exchange_journal_id.default_credit_account_id.id
                name = 'Currency exchange rate difference'
                credit_move_obj = self._generate_credit_move_line(exchange_account_move_id,account_id,credit_amount,
                                                                  amount_currency,name)
                move_line_vals.append(credit_move_obj)
                line = {'account_id': self.invoice_ids[0].account_id.id,
                        'amount_in_company_currency': self.currency_loss_gain_amount,
                        }
                debit_move_obj = self._generate_debit_move_line(exchange_account_move_id, line)
                move_line_vals.append(debit_move_obj)
                exchange_move_obj.line_ids = move_line_vals
                exchange_move_obj.post()
            elif self.currency_loss_gain_type == 'loss':
                self.currency_loss_gain_amount = self.currency_loss_gain_amount*(-1)
                credit_amount = self.currency_loss_gain_amount
                amount_currency = self.currency_loss_gain_amount * self.currency_id.rate
                account_id = self.invoice_ids[0].account_id.id,
                name = "Customer Payment"
                credit_move_obj = self._generate_credit_move_line(exchange_account_move_id, account_id, credit_amount,
                                                                  amount_currency,name)
                move_line_vals.append(credit_move_obj)
                line = {'account_id': self.company_id.currency_exchange_journal_id.default_debit_account_id.id,
                        'amount_in_company_currency': self.currency_loss_gain_amount,
                        }
                debit_move_obj = self._generate_debit_move_line(exchange_account_move_id, line)
                move_line_vals.append(debit_move_obj)
                exchange_move_obj.line_ids = move_line_vals
                exchange_move_obj.post()

        for invoice_id in self.invoice_ids:
            credit_aml_id = [i.id for i in move_obj.line_ids if i.account_id.internal_type in ('receivable', 'payable')]
            invoice_id.assign_outstanding_credit(credit_aml_id)
        self.write({'state': 'approve','account_move_id':move_obj.id})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_analytic_create(self):
        analytic_account_obj = self.env['account.analytic.account']
        analytic_account = analytic_account_obj.create({'name': self.lc_id.name})
        self.analytic_account_id = analytic_account.id
        self.lc_id.analytic_account_id = analytic_account.id
        self.analytic_acc_create = False

    def _generate_move(self,account_move_obj,journal):
        date = self.date[0:10]
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)

        name = journal.with_context(ir_sequence_date=date).sequence_id.next_by_id()
        account_move_id = False
        if not account_move_id:
            account_move_dict = {
                'name': name,
                'date': date,
                'ref': '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
                'operating_unit_id': self.operating_unit_id.id,
            }
            account_move = account_move_obj.create(account_move_dict)
        return account_move

    def _generate_credit_move_line(self,account_move_id,account_id,credit_amount,amount_currency,name):
        date = self.date
        account_move_line_credit = 0, 0, {
            'account_id': account_id,
            'analytic_account_id': self.analytic_account_id.id,
            'credit': credit_amount,
            'amount_currency': -amount_currency,
            'date_maturity': date,
            'debit':  False,
            'name': name,
            'operating_unit_id':  self.operating_unit_id.id,
            'partner_id': self.invoice_ids[0].partner_id.id,
            'move_id': account_move_id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
        }
        # account_move_line_obj.create(account_move_line_credit)
        return account_move_line_credit

    def _generate_debit_move_line(self,account_move_id,line):
        date = self.date
        if 'account_journal_id' in line:
            account_id = line.account_journal_id.default_debit_account_id.id
            name = line.account_journal_id.name
            analytic_account_id = False
            amount_in_company_currency = line.amount_in_company_currency
        elif 'product_id' in line:
            account_id = line.account_id.id
            name = line.product_id.name
            analytic_account_id = self.analytic_account_id.id
            amount_in_company_currency = line.amount_in_company_currency
        else:
            account_id = line['account_id']
            name = 'Currency exchange rate difference'
            analytic_account_id = False
            amount_in_company_currency = line['amount_in_company_currency']
        account_move_line_debit = 0, 0, {
            'account_id': account_id,
            'analytic_account_id': analytic_account_id,
            'credit': False,
            'date_maturity': date,
            'debit': amount_in_company_currency,
            'name': name,
            'operating_unit_id':  self.operating_unit_id.id,
            # 'partner_id': acc_inv_line_obj.partner_id.id,
            'move_id': account_move_id,
            'company_id': self.company_id.id,
        }
        # account_move_line_obj.create(account_move_line_debit)
        return account_move_line_debit

    @api.multi
    def lc_pay_and_reconcile(self, pay_journal,move_obj, pay_amount=None):
        payment_type = self.invoice_ids[0].type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
        if payment_type == 'inbound':
            payment_method = self.env.ref('account.account_payment_method_manual_in')
            journal_payment_methods = pay_journal.inbound_payment_method_ids
        else:
            payment_method = self.env.ref('account.account_payment_method_manual_out')
            journal_payment_methods = pay_journal.outbound_payment_method_ids
        if payment_method not in journal_payment_methods:
            raise UserError(_('No appropriate payment method enabled on journal %s') % pay_journal.name)

        communication = ','.join([i.number for i in self.invoice_ids])

        payment_vals = {
            'invoice_ids': [(6, 0, self.invoice_ids.ids)],
            'amount': pay_amount,
            'payment_date': fields.Date.context_today(self),
            'communication': communication,
            'partner_id': self.invoice_ids[0].partner_id.id,
            'partner_type': self.invoice_ids[0].type in ('out_invoice', 'out_refund') and 'customer' or 'supplier',
            'journal_id': pay_journal.id,
            'payment_type': payment_type,
            'payment_method_id': payment_method.id,
            'name': 'LC Payment',
        }

        payment = self.env['account.payment'].create(payment_vals)
        payment.write({'state': 'posted', 'move_name': move_obj.name})

        return payment


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(LCReceivablePayment, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]


class LCReceivableCollection(models.Model):
    _name = 'lc.receivable.collection'

    collection_parent_id = fields.Many2one('lc.receivable.payment', 'Collections', ondelete='cascade')
    account_journal_id = fields.Many2one('account.journal', string="Bank Account",required=True,
                                         domain="[('type', '=', 'bank')]")
    currency_id = fields.Many2one('res.currency', string='Currency',required=True)
    currency_rate = fields.Float(string='Currency Rate',required=True)
    amount_in_currency = fields.Float(string='Amount In Currency',required=True)
    amount_in_company_currency = fields.Float(string='Base Amount',compute='_compute_rate_amounts',store=True)

    @api.onchange('account_journal_id')
    def _onchange_account_journal_id(self):
        domain = {}
        if not self.collection_parent_id:
            return

        if not self.collection_parent_id.lc_id or not self.collection_parent_id.invoice_ids:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a LC and at lest one Invoice!'),
            }
            return {'warning': warning}

        if self.account_journal_id:
            self.currency_id = self.account_journal_id.currency_id

        domain['currency_id'] = [('id', 'in', (self.collection_parent_id.currency_id.id,
                                               self.collection_parent_id.company_id.currency_id.id))]
        return {'domain': domain}

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.currency_rate = self.collection_parent_id.company_id.currency_id.rate/\
                                 self.currency_id.with_context(date=fields.Date.context_today(self)).rate

    @api.one
    @api.depends('currency_rate','amount_in_currency')
    def _compute_rate_amounts(self):
        for record in self:
            if record.amount_in_currency and record.currency_rate:
                record.amount_in_company_currency = record.amount_in_currency * record.currency_rate


class LCReceivableCharges(models.Model):
    _name = 'lc.receivable.charges'

    charges_parent_id = fields.Many2one('lc.receivable.payment', 'Charges', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Service',required=True,
                                 domain=[('type', '=', 'service')])
    account_id = fields.Many2one('account.account', string="Account")
    currency_id = fields.Many2one('res.currency', string='Currency'
                                  ,required=True)
    currency_rate = fields.Float(string='Currency Rate',required=True)
    amount_in_currency = fields.Float(string='Amount In Currency',required=True)
    amount_in_company_currency = fields.Float(string='Base Amount',compute='_compute_rate_amounts',
                                              store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.charges_parent_id:
            return

        if not self.charges_parent_id.lc_id or not self.charges_parent_id.invoice_ids:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a LC and at lest one Invoice!'),
            }
            return {'warning': warning}

        if self.product_id:
            if not self.product_id.property_account_expense_id:
                raise UserError(_('This service have no expense account. Please set an expense account!'))
            self.account_id = self.product_id.property_account_expense_id

        self.currency_id = self.charges_parent_id.currency_id

        domain['currency_id'] = [('active', '=', True)]
        return {'domain': domain}

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.currency_rate = self.charges_parent_id.company_id.currency_id.rate / \
                                 self.currency_id.with_context(date=fields.Date.context_today(self)).rate

    @api.one
    @api.depends('currency_rate', 'amount_in_currency')
    def _compute_rate_amounts(self):
        for record in self:
            if record.amount_in_currency and record.currency_rate:
                record.amount_in_company_currency = record.amount_in_currency * record.currency_rate