from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorAdvance(models.Model):
    _name = "vendor.advance"
    _description = 'Vendor Advance'
    _order = 'state_order asc,id desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(required=True, copy=False, track_visibility='onchange', string='Name', default='/')
    date = fields.Date(string='Date ', required=True, default=fields.Date.today(), track_visibility='onchange',
                       readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', required=False,
                                 track_visibility='onchange',
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
                                 states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', string='Service/Product', required=False, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 help="Advance Service.")
    advance_amount = fields.Float(string="Approved Advance", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  track_visibility='onchange', help="Finally granted advance amount.")
    adjusted_amount = fields.Float(string="Adjusted Amount", track_visibility='onchange', copy=False,
                                   help="Total amount which are already adjusted in bill.")
    outstanding_amount = fields.Float(string="Outstanding Amount", compute="_compute_outstanding_amount", copy=False,
                                      track_visibility='onchange', help="Remaining Amount to adjustment.", store=True)
    account_id = fields.Many2one('account.account', string="GL Account", required=True, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 help="Account for the advance.")
    description = fields.Char('Particulars', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get())
    active = fields.Boolean(track_visibility='onchange', default=True)
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange',
                               copy=False)
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange', copy=False)
    vat_id = fields.Many2one('account.tax', string='VAT', readonly=True, domain=[('is_vat', '=', True)],track_visibility='onchange',
                             states={'draft': [('readonly', False)]})
    tds_id = fields.Many2one('account.tax', string='TDS', readonly=True, domain=[('is_tds', '=', True)],track_visibility='onchange',
                             states={'draft': [('readonly', False)]})
    security_deposit = fields.Float(string="Security Deposit", readonly=True, default=0.0,
                                    track_visibility='onchange', states={'draft': [('readonly', False)]},
                                    help="Security Deposit.")
    payable_to_supplier = fields.Float('Vendor Payable', readonly=True, store=True, copy=False,
                                       compute="_compute_payable_to_supplier", digits=(16, 2),
                                       help="This is the advance amount after deducting security deposit, Vat and Tax")
    tds_amount = fields.Float('TDS Amount', readonly=True, compute='_compute_amount', copy=False,track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    vat_amount = fields.Float('VAT Amount', compute='_compute_amount', readonly=True, copy=False,track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    total_deduction = fields.Float('Total Deduction', readonly=True, store=True,track_visibility='onchange',
                                   compute='_compute_total_deduction', copy=False,
                                   help='This amount is the summation of Security Deposit, VAT and TDS value')
    adjustable_amount = fields.Float('Adjustable Amount', readonly=True, copy=False,track_visibility='onchange',
                                     compute='_compute_adjustable_amount',
                                     help='This is the adjustable amount in vendor bills')
    in_invoice_ids = fields.One2many('vendor.bill.line', 'advance_id', string='Supplier Invoices',
                                     readonly=True, copy=False)
    journal_id = fields.Many2one('account.move', string='Journal', readonly=True, copy=False,track_visibility='onchange')
    type = fields.Selection([('single', 'Single'), ('multi', 'Multi')],track_visibility='onchange')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Waiting for Approval"),
        ('approve', 'Active'),
        ('done', "Closed"),
        ('cancel', "Canceled"),
        ('inactive', "Inactive"),
        ('expired', "Expired"),
        ('reject', "Rejected")], default='draft', string="Status", copy=False,
        track_visibility='onchange')
    state_order = fields.Integer(compute='_compute_state_order', store=True, readonly=True, copy=False)

    advance_amount_subtotal = fields.Monetary(string='Amount', readonly=True, compute='_compute_amount', store=True)
    initial_outstanding_amount = fields.Float(readonly=True, string='Initial Outstanding Amount', copy=False,
                                              compute='_compute_initial_outstanding_amount', store=True)
    move_ids = fields.One2many('account.move', 'advance_id', string='Journals', copy=False)

    @api.depends('state')
    def _compute_state_order(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state_order = 1
            elif rec.state == 'confirm':
                rec.state_order = 2
            elif rec.state == 'approve':
                rec.state_order = 3
            elif rec.state == 'done':
                rec.state_order = 4
            elif rec.state == 'cancel':
                rec.state_order = 5
            elif rec.state == 'inactive':
                rec.state_order = 6
            elif rec.state == 'expired':
                rec.state_order = 7
            elif rec.state == 'reject':
                rec.state_order = 8

    @api.one
    @api.depends('advance_amount', 'vat_id', 'tds_id', 'product_id', 'partner_id', 'currency_id', 'company_id', 'date')
    def _compute_amount(self):
        tds_amount = self.calculate_tds_amount() if self.tds_id and self.tds_id.amount_type != 'slab' and not self.tds_id.price_include else 0.0
        taxes = False
        if self.vat_id and self.type == 'single':
            advance_amount = self.advance_amount + tds_amount
            taxes = self.vat_id.compute_all(advance_amount, self.currency_id, 1, product=self.product_id,
                                            partner=self.partner_id)
            if taxes:
                tax_pool = self.env['account.tax']
                for tax_item in taxes['taxes']:
                    tax_obj = tax_pool.browse(tax_item['id'])
                    if tax_obj.is_reverse:
                        self.vat_amount = tax_item['amount']

        if taxes:
            self.advance_amount_subtotal = taxes['total_excluded']
        else:
            self.advance_amount_subtotal = self.advance_amount + tds_amount if self.type == 'single' else self.advance_amount

        self.tds_amount = self.calculate_tds_amount()

    @api.multi
    def calculate_tds_amount(self):
        tds_amount = 0.0
        if self.tds_id and self.partner_id and self.date and self.type == 'single':
            if self.tds_id.amount_type == 'slab':
                tax_slab = self.env['account.tax.slab.line'].get_prev_slab_inv(self.partner_id, self.tds_id.id,
                                                                               self.date, self.id)
                if self.vat_id.price_include:
                    total_amount = tax_slab['prev_inv_amount'] + (self.advance_amount - self.vat_amount)
                else:
                    total_amount = tax_slab['prev_inv_amount'] + self.advance_amount

                slab_rate = self.env['account.tax.line'].search([('tax_id', '=', self.tds_id.id),
                                                                 ('range_from', '<=', total_amount),
                                                                 ('range_to', '>=', total_amount)])

                curr_tds_amount = total_amount * (slab_rate.rate / 100)
                remain_tds_amount = curr_tds_amount - tax_slab['prev_tds_amount']
                if remain_tds_amount < 0.0:
                    tds_amount = 0.0
                elif remain_tds_amount > self.advance_amount:
                    tds_amount = self.advance_amount
                else:
                    tds_amount = remain_tds_amount
            else:
                base_val = self.advance_amount if self.tds_id.effect_base_price else self.advance_amount_subtotal

                if self.tds_id.price_include:
                    tds_amount = base_val - (base_val / (1 + self.tds_id.amount / 100))
                elif self.tds_id.price_exclude:
                    tds_amount = (base_val / (1 - self.tds_id.amount / 100)) - base_val
                else:
                    tds_amount = base_val * self.tds_id.amount / 100

        return tds_amount

    @api.depends('advance_amount_subtotal', 'vat_id', 'tds_id', 'vat_amount', 'tds_amount')
    def _compute_initial_outstanding_amount(self):
        for record in self:
            debit_amount = record.advance_amount_subtotal
            if record.type == 'single':
                if len(record.vat_id.children_tax_ids) > 0:
                    for ctax in record.vat_id.children_tax_ids:
                        if ctax.include_in_expense:
                            debit_amount += record.vat_amount
                else:
                    if record.vat_id.include_in_expense:
                        debit_amount += record.vat_amount
                if record.tds_id.include_in_expense:
                    debit_amount += record.tds_amount
            record.initial_outstanding_amount = debit_amount

    @api.one
    @api.depends('security_deposit', 'tds_amount', 'vat_amount')
    def _compute_total_deduction(self):
        for record in self:
            record.total_deduction = record.security_deposit + record.tds_amount + record.vat_amount

    @api.one
    @api.depends('advance_amount', 'total_deduction', 'vat_id', 'tds_id', 'type', 'initial_outstanding_amount', 'security_deposit')
    def _compute_payable_to_supplier(self):
        for record in self:
            if record.type == 'single':
                payable_to_supplier = record.initial_outstanding_amount - record.total_deduction
                record.payable_to_supplier = payable_to_supplier
            else:
                record.payable_to_supplier = record.advance_amount

    @api.one
    @api.depends('advance_amount', 'adjusted_amount')
    def _compute_adjustable_amount(self):
        for record in self:
            record.adjustable_amount = record.advance_amount - record.adjusted_amount

    @api.one
    @api.depends('adjusted_amount', 'initial_outstanding_amount', 'state', 'advance_amount', 'type')
    def _compute_outstanding_amount(self):
        for va in self:
            if va.state not in ('draft', 'confirm', 'cancel'):
                if va.type == 'single':
                    va.outstanding_amount = va.initial_outstanding_amount - va.adjusted_amount
                else:
                    va.outstanding_amount = va.advance_amount - va.adjusted_amount
            else:
                va.outstanding_amount = 0.0

    @api.one
    def action_confirm(self):
        if self.state == 'draft':
            if self.type == 'single':
                if not self.advance_amount > 0:
                    raise ValidationError(_("[Validation Error] Advance Amount must be greater than Zero!"))
                if self.security_deposit >= self.advance_amount:
                    raise ValidationError(
                        _("[Validation Error] Security Deposit cannot be greater than or equal to advance!"))
            if self.total_deduction > self.advance_amount:
                raise ValidationError(
                    _("[Validation Error] Summation of Security Deposit, VAT and TDS"
                      " cannot be greater than approved advance!"))
            sequence = self.get_seq()
            self.write({
                'state': 'confirm',
                'name': sequence,
                'maker_id': self.env.user.id
            })

    @api.one
    def action_validate(self):
        if self.state == 'confirm':
            if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))

            if self.type == 'single' and self.security_deposit > 0:
                self.create_security_deposit()
            journal_type = self.env.ref('vendor_advance.vendor_advance_journal')
            move = self.create_journal(journal_type)
            if move:
                if self.tds_id and self.tds_id.amount_type == 'slab' and self.type == 'single':
                    self.create_slab()

                self.write({
                    'state': 'approve',
                    'approver_id': self.env.user.id,
                    'journal_id': move.id,
                })

    def create_slab(self):
        fy = self.env['account.tax.slab.line'].get_fy(self.date)

        if self.vat_id.price_include:
            invoice_amount = self.advance_amount - self.vat_amount
        else:
            invoice_amount = self.advance_amount

        create = {
            'invoice_amount': invoice_amount,
            'tds_amount': self.tds_amount,
            'partner_id': self.partner_id.id,
            'tax_id': self.tds_id.id,
            'tax_fy_id': fy.id,
            'date': self.date,
            'vendor_advance_id': self.id,
        }
        self.env['account.tax.slab.line'].create(create)

    @api.one
    def toggle_active(self):
        for rec in self:
            super(VendorAdvance, self).toggle_active()
            if not rec.active:
                security_deposit = self.env['vendor.security.deposit'].search([('name', '=', rec.name)], limit=1)
                if security_deposit:
                    security_deposit.write({'active': False, 'state': 'inactive'})
                rec.write({'state': 'inactive'})
            else:
                security_deposit = self.env['vendor.security.deposit'].search([('name', '=', rec.name),
                                                                               ('active', '=', False)], limit=1)
                if security_deposit:
                    security_deposit.write({'active': True, 'state': 'approve'})
                rec.write({'state': 'approve'})

    @api.multi
    def action_draft(self):
        if self.state == 'cancel':
            self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        if self.state == 'confirm':
            self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorAdvance, self).unlink()

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', 'not in', ['cancel', 'draft']),
                 '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.constrains('advance_amount')
    def check_advance_amount(self):
        if self.advance_amount < 0:
            raise ValidationError(
                "Please Check Your Advance Amount!! \n Amount Never Take Negative Value!")

    @api.constrains('security_deposit')
    def check_security_deposit(self):
        if self.security_deposit < 0:
            raise ValidationError(_("[Validation Error] Security Deposit can not be negative value"))

    # @api.model
    # def _needaction_domain_get(self):
    #     return [('state', '=', 'confirm')]

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.product_id:
                name = u'%s [%s]' % (agr.name, agr.product_id.name)
            res.append((agr.id, name))
        return res

    def get_seq(self):
        sequence = ''
        if self.type == 'single':
            sequence = self.env['ir.sequence'].next_by_code('vendor.advance') or ''
        return sequence

    def create_security_deposit(self):
        security_deposit_data = self.get_security_deposit_data()
        res = self.env['vendor.security.deposit'].create(security_deposit_data)
        return res

    def get_security_deposit_data(self):
        security_deposit_data = {
            'partner_id': self.partner_id.id,
            'amount': self.security_deposit,
            'account_id': self.company_id.security_deposit_account_id.id,
            'date': self.date,
            'state': 'approve',
            'name': self.name,
            'description': self.description or 'Vendor Advance'
        }
        return security_deposit_data

    def create_journal(self, journal_id):
        ogl_data = {}
        ogl_data['journal_id'] = journal_id.id
        ogl_data['date'] = self.date if self.date else fields.date.today()
        ogl_data['state'] = 'draft'
        ogl_data['name'] = self.name
        ogl_data['partner_id'] = self.partner_id.id
        ogl_data['company_id'] = self.company_id.id
        ogl_data['advance_id'] = self.id

        journal_item_data = []
        debit_item_data = self.get_debit_item_data(journal_id)
        debit_item = [0, 0, debit_item_data]
        journal_item_data.append(debit_item)

        supplier_credit_amount = debit_item_data['debit']
        if self.type == 'single':
            if self.security_deposit and self.security_deposit > 0:
                deposit_credit_item_data = self.get_deposit_credit_item_data(journal_id)
                deposit_credit_item = [0, 0, deposit_credit_item_data]
                journal_item_data.append(deposit_credit_item)
                supplier_credit_amount = supplier_credit_amount - self.security_deposit

            if self.vat_id:
                if self.vat_id.amount_type == 'group':
                    for child_vat in self.vat_id.children_tax_ids:
                        vat_item_data = self.get_vat_item_data(child_vat, self.vat_amount)
                        vat_item = [0, 0, vat_item_data]
                        journal_item_data.append(vat_item)

                        if vat_item:
                            if child_vat.is_reverse:
                                supplier_credit_amount = supplier_credit_amount - self.vat_amount
                            else:
                                supplier_credit_amount = supplier_credit_amount + self.vat_amount
                else:
                    vat_item_data = self.get_vat_item_data(self.vat_id, self.vat_amount)
                    vat_item = [0, 0, vat_item_data]
                    journal_item_data.append(vat_item)

                    if vat_item:
                        if self.vat_id.is_reverse:
                            supplier_credit_amount = supplier_credit_amount - self.vat_amount
                        else:
                            supplier_credit_amount = supplier_credit_amount + self.vat_amount

            if self.tds_id:
                tds_item_data = self.get_tds_item_data(self.tds_id, self.tds_amount)
                tds_item = [0, 0, tds_item_data]
                journal_item_data.append(tds_item)
                if tds_item:
                    if self.tds_id.is_reverse:
                        supplier_credit_amount = supplier_credit_amount - self.tds_amount
                    else:
                        supplier_credit_amount = supplier_credit_amount + self.tds_amount

        supplier_credit_item_data = self.get_supplier_credit_item_data(journal_id, supplier_credit_amount)
        supplier_credit_item = [0, 0, supplier_credit_item_data]
        journal_item_data.append(supplier_credit_item)
        ogl_data['line_ids'] = journal_item_data
        move = self.env['account.move'].create(ogl_data)
        move.sudo().post()

        return move

    def get_debit_item_data(self, journal_id):
        debit_amount = self.advance_amount_subtotal
        if self.type == 'single':
            if len(self.vat_id.children_tax_ids) > 0:
                for ctax in self.vat_id.children_tax_ids:
                    if ctax.include_in_expense:
                        debit_amount += self.vat_amount
            else:
                if self.vat_id.include_in_expense:
                    debit_amount += self.vat_amount
            if self.tds_id.include_in_expense:
                debit_amount += self.tds_amount
        # self.initial_outstanding_amount = debit_amount
        debit_item_data = {
            'name': self.description or 'Vendor Advance',
            'ref': self.name,
            'date': self.date if self.date else fields.date.today(),
            'account_id': self.account_id.id,
            'debit': debit_amount,
            'credit': 0.0,
            'company_id': self.company_id.id

        }
        return debit_item_data

    def get_deposit_credit_item_data(self, journal_id):
        deposit_credit_item = {
            'name': self.description or 'Vendor Advance',
            'ref': self.name,
            'date': self.date if self.date else fields.date.today(),
            'account_id': self.company_id.security_deposit_account_id.id,
            'debit': 0.0,
            'credit': self.security_deposit,
            'company_id': self.company_id.id

        }
        return deposit_credit_item

    def get_vat_item_data(self, vat_id, vat_amount):
        vat_item_data = {
            'name': self.description or 'Vendor Advance',
            'ref': self.name,
            'date': self.date if self.date else fields.date.today(),
            'account_id': vat_id.account_id.id,
            'company_id': self.company_id.id,
            'tax_line_id': vat_id.id,
            'tax_type': 'vat',
            'is_tdsvat_payable': True,
            'product_id': self.product_id.id
        }
        if vat_id.is_reverse:
            vat_item_data['debit'] = 0.0
            vat_item_data['credit'] = vat_amount
        else:
            vat_item_data['debit'] = vat_amount
            vat_item_data['credit'] = 0.0
        return vat_item_data

    def get_tds_item_data(self, tds_id, tds_amount):
        tds_item_data = {
            'name': self.description or 'Vendor Advance',
            'ref': self.name,
            'date': self.date if self.date else fields.date.today(),
            'account_id': self.tds_id.account_id.id,
            'company_id': self.company_id.id,
            'tax_line_id': tds_id.id,
            'tax_type': 'tds',
            'is_tdsvat_payable': True,
            'product_id': self.product_id.id
        }
        if tds_id.is_reverse:
            tds_item_data['debit'] = 0.0
            tds_item_data['credit'] = tds_amount
        else:
            tds_item_data['debit'] = tds_amount
            tds_item_data['credit'] = 0.0
        return tds_item_data

    def get_supplier_credit_item_data(self, journal_id, supplier_credit_amount):
        supplier_credit_item = {
            'name': self.description or 'Vendor Advance',
            'ref': self.name,
            'date': self.date if self.date else fields.date.today(),
            'account_id': self.partner_id.property_account_payable_id.id,
            'debit': 0.0,
            'credit': supplier_credit_amount,
            'company_id': self.company_id.id

        }
        return supplier_credit_item


class VendorBillLine(models.Model):
    _name = 'vendor.bill.line'

    advance_id = fields.Many2one('vendor.advance', string="Vendor Advance", copy=False)
    invoice_id = fields.Many2one('account.invoice', string="Bill No.", copy=False)
    adjusted_amount = fields.Float('Adjusted Amount')
    billing_date = fields.Date('Billing Date')
