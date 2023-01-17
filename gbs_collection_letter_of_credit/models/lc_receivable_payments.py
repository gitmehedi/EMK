from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime


class LCReceivablePayment(models.Model):
    _name = 'lc.receivable.payment'
    _description = 'LC Receivable Payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "date desc"

    name = fields.Char(string='Reference', readonly=True, index=True, default='Draft',
                       track_visibility='onchange')
    lc_id = fields.Many2one('letter.credit', 'LC', ondelete='cascade', required=True,
                            readonly=True, states={'draft': [('readonly', False)]},
                            domain=[('type', '=', 'export')],
                            track_visibility='onchange')
    shipment_id = fields.Many2one('purchase.shipment', 'Shipment', ondelete='cascade', required=True,
                                  readonly=True, states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, store=True,
                                  track_visibility='onchange', compute='_compute_rate_amounts')
    invoice_amount = fields.Float(string='Invoice Amount', readonly=True, store=True,
                                  digits=dp.get_precision('Account'),
                                  track_visibility='onchange', compute='_compute_rate_amounts')
    currency_rate = fields.Float(string='Currency Rate', readonly=True, store=True,
                                 track_visibility='onchange', compute='_compute_rate_amounts')
    amount_in_company_currency = fields.Float(string='Base Amount', readonly=True, store=True,
                                              digits=dp.get_precision('Account'),
                                              track_visibility='onchange', compute='_compute_rate_amounts')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Profit Centre', ondelete="cascade",
                                          readonly=True, states={'draft': [('readonly', False)]},
                                          track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', readonly=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    date = fields.Datetime('Date', index=True, default=fields.Datetime.now,
                           readonly=True, states={'draft': [('readonly', False)]},
                           track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Posted'),
                              ('cancel', 'Cancelled')], string='Status', default='draft',
                             track_visibility='onchange')
    invoice_ids = fields.Many2many('account.invoice',
                                   'lc_collection_invoice_rel',
                                   'lc_collection_id',
                                   'invoice_id',
                                   'Invoices', readonly=True, required=True,
                                   states={'draft': [('readonly', False)]})
    currency_loss_gain_amount = fields.Float(string='Loss/Gain Amount', compute='_compute_currency_loss_gain',
                                             track_visibility='onchange', digits=dp.get_precision('Account'))
    currency_loss_gain_type = fields.Selection([('margin', 'Margin'),
                                                ('loss', 'Loss'),
                                                ('gain', 'Gain'), ], string='Loss/Gain Type', default='margin',
                                               compute='_compute_currency_loss_gain',
                                               track_visibility='onchange')
    particular = fields.Char(string='Particular', readonly=True, states={'draft': [('readonly', False)]},
                             track_visibility='onchange')
    analytic_acc_create = fields.Boolean('Need to create Analytic Account', default=False)
    journal_id = fields.Many2one('account.journal', string='Account Journal', ondelete="cascade",
                                 domain=[('type', '=', 'lc')], required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, track_visibility='onchange')
    reference = fields.Text(string='Reference', compute='_compute_reference', readonly=True, store=False)
    bank_ref = fields.Char(string='Bank Reference', readonly=True, states={'draft': [('readonly', False)]},
                           track_visibility='onchange')
    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    """ Relational Fields """
    lc_receivable_collection_ids = fields.One2many('lc.receivable.collection', 'collection_parent_id',
                                                   string="Collections", readonly=True,
                                                   states={'draft': [('readonly', False)]})
    lc_receivable_charges_ids = fields.One2many('lc.receivable.charges', 'charges_parent_id',
                                                string="Charges", readonly=True,
                                                states={'draft': [('readonly', False)]})
    lc_receivable_miscellaneous_ids = fields.One2many('lc.receivable.miscellaneous', 'miscellaneous_parent_id',
                                                      string='Miscellaneous', readonly=True,
                                                      states={'draft': [('readonly', False)]})
    narration = fields.Text(string='Narration', readonly=True, states={'draft': [('readonly', False)]},
                            track_visibility='onchange')
    ibp_loan = fields.Float(string='IBP Loan', store=True, digits=dp.get_precision('Account'), )

    @api.constrains('lc_receivable_collection_ids')
    def constrains_lc_receivable_collection_ids(self):
        if len(self.lc_receivable_collection_ids.ids) <= 0:
            raise ValidationError(_('You have to provide Fund Transfer'))

        if any(c.amount_in_currency < 0 for c in self.lc_receivable_collection_ids):
            raise ValidationError(_('Amount In Currency of Fund Transfer cannot be negative!!'))

        if any(c.amount_in_company_currency < 0 for c in self.lc_receivable_collection_ids):
            raise ValidationError(_('BDT Amount of Fund Transfer cannot be negative!!'))

    @api.constrains('lc_receivable_charges_ids')
    def constrains_lc_receivable_charges_ids(self):
        if any(c.amount_in_currency < 0 for c in self.lc_receivable_charges_ids):
            raise ValidationError(_('Amount In Currency of Charges cannot be negative!!'))

        if any(c.amount_in_company_currency < 0 for c in self.lc_receivable_charges_ids):
            raise ValidationError(_('BDT Amount of Charges cannot be negative!!'))

    @api.constrains('lc_receivable_miscellaneous_ids')
    def constrains_lc_receivable_miscellaneous_ids(self):
        if any(c.amount_in_currency < 0 for c in self.lc_receivable_miscellaneous_ids):
            raise ValidationError(_('Amount In Currency of Loan/Exchange cannot be negative!!'))

        if any(c.amount_in_company_currency < 0 for c in self.lc_receivable_miscellaneous_ids):
            raise ValidationError(_('BDT Amount of Loan/Exchange cannot be negative!!'))

    @api.onchange('narration')
    def onchange_narration(self):
        if self.narration:
            self.narration = self.narration.strip()

    @api.onchange('lc_id', 'journal_id')
    def onchange_lc_id_shipment(self):
        if self.lc_id:
            shipment_ids = []
            shipment_objs = self.env['purchase.shipment'].search([('lc_id', '=', self.lc_id.id)])
            if shipment_objs:
                shipment_ids = shipment_objs.ids
            return {
                'domain': {'shipment_id': [('id', 'in', shipment_ids)]}
            }

    @api.onchange('lc_id', 'journal_id')
    def onchange_lc_id(self):
        if self.lc_id:
            self.operating_unit_id = self.lc_id.operating_unit_id.id
            self.shipment_id = []
            self.invoice_ids = []
            self.currency_id = []
            self.invoice_amount = []
            self.amount_in_company_currency = []
            self.lc_receivable_collection_ids = []
            self.lc_receivable_charges_ids = []
            self.lc_receivable_miscellaneous_ids = []
            self.analytic_account_id = False
            self.analytic_acc_create = False
            invoice_ids = []
            shipment_ids = []
            shipment_objs = self.env['purchase.shipment'].search([('lc_id', '=', self.lc_id.id)])
            if shipment_objs:
                shipment_ids = shipment_objs.ids

            if self.lc_id.pi_ids_temp:
                so_objs = self.env['sale.order'].search([('pi_id', 'in', self.lc_id.pi_ids_temp.ids)])
                if so_objs:
                    for so_obj in so_objs:
                        for invoice_id in so_obj.invoice_ids:
                            if invoice_id.so_id:
                                invoice_ids.append(invoice_id.id)
            analytic_account_id = False
            if self.lc_id.analytic_account_id:
                analytic_account_id = self.lc_id.analytic_account_id.id
                self.analytic_account_id = analytic_account_id
            else:
                self.analytic_acc_create = True
            return {
                'domain': {'invoice_ids': [('id', 'in', invoice_ids),
                                           ('currency_id', '=', self.lc_id.currency_id.id),
                                           ('state', '=', 'open')],
                           'analytic_account_id': [('id', '=', analytic_account_id)]
                           }
            }

    @api.multi
    @api.depends('lc_id', 'date', 'invoice_ids')
    def _compute_rate_amounts(self):
        for rec in self:
            if rec.lc_id and rec.invoice_ids:
                rec.currency_id = rec.lc_id.currency_id.id
                rec.invoice_amount = sum(inv.residual for inv in rec.invoice_ids)

                to_currency = rec.company_id.currency_id
                from_currency = rec.invoice_ids[0].currency_id.with_context(
                    date=rec.invoice_ids[0]._get_currency_rate_date() or fields.Date.context_today(rec.invoice_ids[0]))

                # Set currency rate of a LC Collection
                rec.currency_rate = to_currency.round(to_currency.rate / from_currency.rate)

                # calculate total invoice amount in company currency
                amount_in_company_currency = 0
                for inv in rec.invoice_ids:
                    from_currency = inv.currency_id.with_context(
                        date=inv._get_currency_rate_date() or fields.Date.context_today(inv))
                    amount_in_company_currency += inv.residual * to_currency.round(
                        to_currency.rate / from_currency.rate)

                # Set the Base Amount of a LC Collection
                rec.amount_in_company_currency = amount_in_company_currency

    @api.multi
    @api.depends('lc_receivable_collection_ids.amount_in_company_currency',
                 'lc_receivable_charges_ids.amount_in_company_currency',
                 'lc_receivable_miscellaneous_ids.amount_in_company_currency')
    def _compute_currency_loss_gain(self):
        for rec in self:
            total_collection_amount = 0.0
            total_charges_amount = 0.0
            total_miscellaneous_amount = 0.0
            if rec.lc_receivable_collection_ids:
                total_collection_amount = sum(
                    line.amount_in_company_currency for line in rec.lc_receivable_collection_ids)
            if rec.lc_receivable_charges_ids:
                total_charges_amount = sum(line.amount_in_company_currency for line in rec.lc_receivable_charges_ids)
            if rec.lc_receivable_miscellaneous_ids:
                total_miscellaneous_amount = sum(
                    line.amount_in_company_currency for line in rec.lc_receivable_miscellaneous_ids)

            rec.currency_loss_gain_amount = (
                                                        total_collection_amount + total_charges_amount + total_miscellaneous_amount) - rec.amount_in_company_currency

            # if -1 < rec.currency_loss_gain_amount < 1:
            #     rec.currency_loss_gain_amount = 0
            #
            # if rec.currency_loss_gain_amount >= rec.amount_in_company_currency:
            #     rec.currency_loss_gain_amount = 0.0
            # if rec.currency_loss_gain_amount < 0:
            #     rec.currency_loss_gain_type = 'loss'
            # elif rec.currency_loss_gain_amount > 0:
            #     rec.currency_loss_gain_type = 'gain'
            # else:
            #     rec.currency_loss_gain_type = 'margin'

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
        if self.state == 'approve':
            return

        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        move_obj = self.env['account.move']
        move = self._generate_move(move_obj, self.journal_id)

        # credit part
        name = self.narration
        account_id = self.invoice_ids[0].account_id.id
        amount_currency = self.invoice_amount if self.currency_id.id != self.company_id.currency_id.id else 0
        currency_id = self.currency_id.id if self.currency_id.id != self.company_id.currency_id.id else False

        credit = 0.0
        credit += sum(collection.amount_in_company_currency for collection in self.lc_receivable_collection_ids)
        credit += sum(charge.amount_in_company_currency for charge in self.lc_receivable_charges_ids)
        credit += sum(misc.amount_in_company_currency for misc in self.lc_receivable_miscellaneous_ids)

        credit_aml_dict = self._generate_credit_move_line(move.id, account_id, credit, amount_currency, name,
                                                          currency_id)
        aml_obj.create(credit_aml_dict)

        # debit part
        for collection in self.lc_receivable_collection_ids:
            account_id = collection.account_journal_id.default_debit_account_id.id
            debit = collection.amount_in_company_currency
            amount_currency = collection.amount_in_currency
            name = collection.account_journal_id.name
            currency_id = collection.currency_id.id

            debit_aml_dict = self._generate_debit_move_line(move.id, account_id, debit, amount_currency, name,
                                                            currency_id)
            aml_obj.create(debit_aml_dict)

        for charge in self.lc_receivable_charges_ids:
            account_id = charge.account_id.id
            debit = charge.amount_in_company_currency
            amount_currency = charge.amount_in_currency
            name = charge.product_id.name
            currency_id = charge.currency_id.id

            debit_aml_dict = self._generate_debit_move_line(move.id, account_id, debit, amount_currency, name,
                                                            currency_id)
            debit_aml_dict.update({'analytic_account_id': self.analytic_account_id.id,
                                   'cost_center_id': self.lc_id.product_lines[0].product_id.cost_center_id.id})
            aml_obj.create(debit_aml_dict)

        for misc in self.lc_receivable_miscellaneous_ids:
            account_id = misc.account_id.id
            debit = misc.amount_in_company_currency
            amount_currency = misc.amount_in_currency
            name = misc.narration
            currency_id = misc.currency_id.id

            debit_aml_dict = self._generate_debit_move_line(move.id, account_id, debit, amount_currency, name,
                                                            currency_id)
            debit_aml_dict.update({'analytic_account_id': self.analytic_account_id.id,
                                   'cost_center_id': self.lc_id.product_lines[0].product_id.cost_center_id.id})
            aml_obj.create(debit_aml_dict)

        # post journal entries
        move.post()

        self.lc_pay_and_reconcile(self.journal_id, move, credit)

        for invoice in self.invoice_ids:
            credit_aml_id = [i.id for i in move.line_ids if i.account_id.internal_type in ('receivable', 'payable')]
            invoice.assign_outstanding_credit(credit_aml_id)

        self.write({'state': 'approve', 'account_move_id': move.id})

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

    def _generate_move(self, move_obj, journal):
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'),
                            _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)

        date = self.date[0:10]
        name = journal.with_context(ir_sequence_date=date).sequence_id.next_by_id()
        move_dict = {
            'name': name,
            'date': date,
            'ref': self.lc_id.name,
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'operating_unit_id': self.operating_unit_id.id
        }
        move = move_obj.create(move_dict)

        return move

    def _generate_credit_move_line(self, move_id, account_id, credit, amount_currency, name, currency_id):
        return {
            'account_id': account_id,
            'analytic_account_id': self.analytic_account_id.id,
            'date_maturity': self.date,
            'amount_currency': -amount_currency,
            'credit': credit,
            'debit': False,
            'name': name,
            'operating_unit_id': self.operating_unit_id.id,
            'partner_id': self.lc_id.second_party_applicant.id,
            'move_id': move_id,
            'currency_id': currency_id
        }

    def _generate_debit_move_line(self, move_id, account_id, debit, amount_currency, name, currency_id):
        return {
            'account_id': account_id,
            'date_maturity': self.date,
            'amount_currency': amount_currency,
            'credit': False,
            'debit': debit,
            'name': name,
            'operating_unit_id': self.operating_unit_id.id,
            'partner_id': self.lc_id.second_party_applicant.id,
            'move_id': move_id,
            'currency_id': currency_id
        }

    @api.multi
    def lc_pay_and_reconcile(self, pay_journal, move_obj, pay_amount=None):
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

    @api.model
    def create(self, vals):
        if 'operating_unit_id' not in vals:
            lc = self.env['letter.credit'].search([('id', '=', vals['lc_id'])])
            vals['operating_unit_id'] = lc.operating_unit_id.id

        if 'ibp_loan' not in vals:
            vals['ibp_loan'] = self._get_value_ibp_load(vals['analytic_account_id'], vals['date'])
        return super(LCReceivablePayment, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'lc_id' in vals:
            lc = self.env['letter.credit'].search([('id', '=', vals['lc_id'])])
            vals['operating_unit_id'] = lc.operating_unit_id.id

        return super(LCReceivablePayment, self).write(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(LCReceivablePayment, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    @api.onchange('analytic_account_id')
    def _get_value_ibp_load(self, _analytic_account_id=None, _date=None):

        analytic_account_id = _analytic_account_id
        date = _date
        ReportUtility = self.env['report.utility']
        if date is None:
            date = self.date
        # a = ReportUtility.get_date_from_string(date)
        #
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
        if analytic_account_id is None:
            analytic_account_id = self.analytic_account_id.id
        query = """select dr.date_start as date_start, dr.date_end as date_end from date_range as dr
                                        LEFT JOIN date_range_type as drt ON drt.id = dr.type_id 
                                        where fiscal_year=True 
                                        and '%s' between dr.date_start and dr.date_end""" % date
        self.env.cr.execute(query)
        fiscal_year_date = self.env.cr.dictfetchall()
        start_date = ReportUtility.get_date_from_string(fiscal_year_date[0]['date_start'])
        end_date = ReportUtility.get_date_from_string(fiscal_year_date[0]['date_end'])

        if analytic_account_id:
            query = ("select SUM(aml.debit)-SUM(aml.credit) as ibp_loan from account_move_line as aml "
                     "LEFT JOIN account_move as am ON am.id = aml.move_id "
                     "LEFT JOIN account_account as aa ON aa.id=aml.account_id "
                     "LEFT JOIN account_account_type as aat ON aat.id = aa.user_type_id "
                     "WHERE aml.analytic_account_id={0} and aat.is_ibp_loan=True and am.state='posted' and '{1}' between '{2}' and '{3}'").format(
                analytic_account_id, date, start_date, end_date)
            self.env.cr.execute(query)
            ibp_loan_data = self.env.cr.dictfetchall()

            ibp_loan = ibp_loan_data[0]['ibp_loan']
            if not ibp_loan:
                ibp_loan = 0
            if _analytic_account_id is None:
                self.ibp_loan = ibp_loan
            else:
                return ibp_loan


class LCReceivableCollection(models.Model):
    _name = 'lc.receivable.collection'

    collection_parent_id = fields.Many2one('lc.receivable.payment', 'Collections', ondelete='cascade')
    account_journal_id = fields.Many2one('account.journal', string="Bank Account", required=True,
                                         domain="[('type', '=', 'bank')]")
    currency_id = fields.Many2one('res.currency', string='Currency')
    currency_rate = fields.Float(string='Currency Rate')
    amount_in_currency = fields.Float(string='Amount In Currency', digits=dp.get_precision('Account'))
    # amount_in_company_currency = fields.Float(string='Base Amount',compute='_compute_rate_amounts',
    #                                           digits=dp.get_precision('Account'),store=True)
    amount_in_company_currency = fields.Float(string='Base Amount', digits=dp.get_precision('Account'))

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
            if self.account_journal_id.currency_id.id and self.account_journal_id.currency_id.id != self.collection_parent_id.company_id.currency_id.id:
                self.currency_id = self.account_journal_id.currency_id

        domain['currency_id'] = [('active', '=', True),
                                 ('id', '!=', self.collection_parent_id.company_id.currency_id.id)]
        return {'domain': domain}

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.currency_rate = self.collection_parent_id.company_id.currency_id.rate / \
                                 self.currency_id.with_context(date=fields.Date.context_today(self)).rate

    @api.onchange('currency_id', 'currency_rate', 'amount_in_currency')
    def _onchange_amount_in_company_currency(self):
        if self.amount_in_currency and self.currency_rate and self.currency_id.id:
            self.amount_in_company_currency = self.amount_in_currency * self.currency_rate


class LCReceivableCharges(models.Model):
    _name = 'lc.receivable.charges'

    charges_parent_id = fields.Many2one('lc.receivable.payment', 'Charges', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Service', required=True,
                                 domain=[('type', '=', 'service')])
    account_id = fields.Many2one('account.account', string="Account")
    currency_id = fields.Many2one('res.currency', string='Currency')
    currency_rate = fields.Float(string='Currency Rate')
    amount_in_currency = fields.Float(string='Amount In Currency', digits=dp.get_precision('Account'))
    amount_in_company_currency = fields.Float(string='Base Amount', digits=dp.get_precision('Account'))

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

        domain['currency_id'] = [('active', '=', True), ('id', '!=', self.charges_parent_id.company_id.currency_id.id)]
        return {'domain': domain}

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.currency_rate = self.charges_parent_id.company_id.currency_id.rate / \
                                 self.currency_id.with_context(date=fields.Date.context_today(self)).rate

    @api.onchange('currency_id', 'currency_rate', 'amount_in_currency')
    def _onchange_amount_in_company_currency(self):
        if self.amount_in_currency and self.currency_rate and self.currency_id.id:
            self.amount_in_company_currency = self.amount_in_currency * self.currency_rate


class LCReceivableMiscellaneous(models.Model):
    _name = 'lc.receivable.miscellaneous'

    # relational field
    miscellaneous_parent_id = fields.Many2one('lc.receivable.payment', 'Miscellaneous', ondelete='cascade')

    narration = fields.Text(string='Narration', required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    currency_rate = fields.Float(string='Currency Rate')
    amount_in_currency = fields.Float(string='Amount In Currency', digits=dp.get_precision('Account'))
    amount_in_company_currency = fields.Float(string='Base Amount', digits=dp.get_precision('Account'))

    @api.onchange('account_id')
    def _onchange_account_id(self):
        domain = dict()
        if not self.miscellaneous_parent_id:
            return

        if not self.miscellaneous_parent_id.lc_id or not self.miscellaneous_parent_id.invoice_ids:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a LC and at lest one Invoice!'),
            }
            return {'warning': warning}

        domain['currency_id'] = [('active', '=', True),
                                 ('id', '!=', self.miscellaneous_parent_id.company_id.currency_id.id)]
        return {'domain': domain}

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.currency_rate = self.miscellaneous_parent_id.company_id.currency_id.rate / \
                                 self.currency_id.with_context(date=fields.Date.context_today(self)).rate

    @api.onchange('currency_id', 'currency_rate', 'amount_in_currency')
    def _onchange_amount_in_company_currency(self):
        if self.amount_in_currency and self.currency_rate and self.currency_id.id:
            self.amount_in_company_currency = self.amount_in_currency * self.currency_rate
