from odoo import api, fields, models, _
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
    amount_in_company_currency = fields.Float(string='Amount',readonly=True,store=True,
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
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled')], string='Status', default='draft',
                             track_visibility='onchange')

    invoice_ids = fields.Many2many('account.invoice',
                                   'lc_collection_invoice_rel',
                                   'lc_collection_id',
                                   'invoice_id',
                                   'Invoices',readonly=True,required=True,
                                   states={'draft': [('readonly', False)]})

    currency_loss_gain_amount = fields.Float(string='Loss/Gain Amount',compute='_compute_currency_gain_loss_amount',
                                             track_visibility='onchange')
    currency_loss_gain_type = fields.Selection([('margin', 'Margin'),
                                                ('loss', 'Loss'),
                                                ('gain', 'Gain'),], string='Loss/Gain Type', default='margin',
                                               compute='_compute_currency_gain_loss_amount',
                                               track_visibility='onchange')
    particular = fields.Char(string='Particular', readonly=True, states={'draft': [('readonly', False)]},
                             track_visibility='onchange')
    analytic_acc_create = fields.Boolean('Need to create Analytic Account',default=False)

    journal_id = fields.Many2one('account.journal', string='Account Journal', ondelete="cascade",
                                 required=True,readonly=True,states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')

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
                record.currency_rate = \
                    record.company_id.currency_id.rate / record.currency_id.with_context(date=record.date).rate
                record.amount_in_company_currency = record.invoice_amount * record.currency_rate

    @api.multi
    @api.depends('lc_receivable_collection_ids.amount_in_company_currency',
                 'lc_receivable_charges_ids.amount_in_company_currency')
    def _compute_currency_gain_loss_amount(self):
        for rec in self:
            total_collection_amount = 0.0
            total_charges_amount = 0.0
            if rec.lc_receivable_collection_ids:
                total_collection_amount = sum(line.amount_in_company_currency for line in rec.lc_receivable_collection_ids)
            if rec.lc_receivable_charges_ids:
                total_charges_amount = sum(line.amount_in_company_currency for line in rec.lc_receivable_charges_ids)

            rec.currency_gain_loss_amount = rec.amount_in_company_currency - (total_collection_amount + total_charges_amount)
            if rec.currency_gain_loss_amount >= rec.amount_in_company_currency:
                rec.currency_gain_loss_amount = 0.0
            if rec.currency_gain_loss_amount < 0:
                rec.currency_loss_gain_type = 'loss'
            elif rec.currency_gain_loss_amount > 0:
                rec.currency_loss_gain_type = 'gain'
            else:
                rec.currency_loss_gain_type = 'margin'

    @api.multi
    def action_confirm(self):
        if not self.analytic_account_id:
            raise UserError(_('Without Analytic Account can not be confirmed!'))
        if self.name == 'draft':
            new_seq = self.env['ir.sequence'].next_by_code('lc.collection.sequence')
            self.name = new_seq
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        # account_move_obj = self.env['account.move']
        # account_move_line_obj = self.env['account.move.line']
        # journal_id =
        # move_obj = self._generate_move(journal_id, self.date, account_move_obj)
        # account_move_id = move_obj.id
        # if self.lc_receivable_collection_ids:
        #     for line in self.lc_receivable_collection_ids:
        #
        #         self._generate_credit_move_line(line,self.date,account_move_id)
        #         self._generate_debit_move_line(line,self.date,account_move_id)
        # if self.lc_receivable_charges_ids:
        #     return
        # if self.currency_loss_gain_type != 'margin':
        #     return
        self.write({'state': 'approve'})

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


    def _generate_move(self, line,date,account_move_obj):
        journal = line.account_journal_id
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

    def _generate_credit_move_line(self,line,date,account_move_id,account_move_line_obj):
        account_move_line_credit = {
            'account_id': self.invoice_ids[0].account_id,
            'analytic_account_id': self.account_analytic_id.id,
            'credit': line.amount_in_currency,
            'date_maturity': date,
            'debit':  False,
            'name': 'Customer Payment',
            'operating_unit_id':  self.operating_unit_id.id,
            # 'partner_id': acc_inv_line_obj.partner_id.id,
            'move_id': account_move_id,
        }
        account_move_line_obj.create(account_move_line_credit)
        return True

    def _generate_debit_move_line(self,journal,acc_inv_line_obj,date,account_move_id,account_move_line_obj):
        account_move_line_debit = {
            'account_id': journal.default_debit_account_id.id,
            'analytic_account_id': acc_inv_line_obj.account_analytic_id.id,
            'credit': False,
            'date_maturity': date,
            'debit':  acc_inv_line_obj.price_subtotal,
            'name': acc_inv_line_obj.name,
            'operating_unit_id':  acc_inv_line_obj.operating_unit_id.id,
            # 'partner_id': acc_inv_line_obj.partner_id.id,
            'move_id': account_move_id,
        }
        account_move_line_obj.create(account_move_line_debit)
        return True


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

        self.currency_id = self.collection_parent_id.currency_id
        self.currency_rate = self.collection_parent_id.currency_rate
        self.amount_in_currency = self.collection_parent_id.invoice_amount

        domain['currency_id'] = [('id', '=', self.collection_parent_id.currency_id.id)]
        return {'domain': domain}

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
            self.account_id = self.product_id.property_account_income_id

        self.currency_id = self.charges_parent_id.currency_id
        self.currency_rate = self.charges_parent_id.currency_rate
        self.amount_in_currency = self.charges_parent_id.invoice_amount

        domain['currency_id'] = [('id', '=', self.charges_parent_id.currency_id.id)]
        return {'domain': domain}

    @api.one
    @api.depends('currency_rate', 'amount_in_currency')
    def _compute_rate_amounts(self):
        for record in self:
            if record.amount_in_currency and record.currency_rate:
                record.amount_in_company_currency = record.amount_in_currency * record.currency_rate