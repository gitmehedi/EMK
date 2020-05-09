from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorAgreement(models.Model):
    _name = "agreement"
    _order = 'name desc,state asc'
    _inherit = ["agreement", 'mail.thread', 'ir.needaction_mixin']

    code = fields.Char(required=False, copy=False, string='Agreement No')
    name = fields.Char(required=False, track_visibility='onchange', string='Advance No', default='/')
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', required=False,
                                 track_visibility='onchange',
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
                                 states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', string='Service/Product', required=False, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 help="Agreement Service.")
    advance_amount = fields.Float(string="Approved Advance", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  track_visibility='onchange', help="Finally granted advance amount.")
    adjusted_amount = fields.Float(string="Adjusted Amount", track_visibility='onchange',
                                   help="Total amount which are already adjusted in bill.")
    outstanding_amount = fields.Float(string="Outstanding Amount", compute='_compute_outstanding_amount', readonly=True,
                                      track_visibility='onchange', help="Remaining Amount to adjustment.")
    account_id = fields.Many2one('account.account', string="GL Account", required=True, readonly=True,
                                 track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 domain=[('level_id.name', '=', 'Layer 5'), ('reconcile', '=', True)],
                                 help="Account for the agreement.")
    description = fields.Text('Particulars', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('agreement'))
    agreement_type = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ], string='Type', required=True,
                                      default='purchase', invisible=True)
    active = fields.Boolean(track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', 'Branch',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, required=True,
                                        states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    type = fields.Selection([('single', 'Single'), ('multi', 'Multi')], default='Type')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('done', "Done"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')
    vat_id = fields.Many2one('account.tax', string='VAT', readonly=True, states={'draft': [('readonly', False)]})
    tds_id = fields.Many2one('tds.rule', string='TDS', readonly=True, states={'draft': [('readonly', False)]})
    security_deposit = fields.Float(string="Security Deposit", readonly=True, default=0.0,
                                    track_visibility='onchange', states={'draft': [('readonly', False)]},
                                    help="Security Deposit.")
    payable_to_supplier = fields.Float('Payable TO Supplier', readonly=True, store=True,
                                       compute="_compute_payable_to_supplier",
                                       help="This is the advance amount after deducting security deposit, Vat and Tax")
    payment_line_ids = fields.One2many('payment.instruction', 'agreement_id', readonly=True, copy=False)
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Advance Paid', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)

    @api.one
    @api.depends('advance_amount', 'security_deposit')
    def _compute_payable_to_supplier(self):
        for record in self:
            record.payable_to_supplier = self.advance_amount - self.security_deposit

    @api.one
    @api.depends('payment_line_ids.amount', 'payment_line_ids.state')
    def _compute_payment_amount(self):
        for va in self:
            va.total_payment_amount = sum(line.amount for line in va.payment_line_ids if line.state not in ['cancel'])
            va.total_payment_approved = sum(line.amount for line in va.payment_line_ids if line.state in ['approved'])

    @api.one
    @api.depends('adjusted_amount', 'total_payment_approved')
    def _compute_outstanding_amount(self):
        for va in self:
            va.outstanding_amount = va.total_payment_approved - va.adjusted_amount

    @api.model
    def create(self, vals):
        return super(VendorAgreement, self).create(vals)

    @api.one
    def action_confirm(self):
        if self.state == 'draft':
            if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
            sequence = ''
            if self.type == 'single':
                sequence = self.env['ir.sequence'].next_by_code('vendor.advance') or ''
            self.write({
                'state': 'confirm',
                'name': sequence,
            })

    @api.one
    def action_validate(self):
        if self.state == 'confirm':
            if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))

            if self.type == 'single':
                security_deposit_env = self.env['vendor.security.deposit']
                security_deposit_env.create({
                    'partner_id': self.partner_id.id,
                    'amount': self.security_deposit,
                    'account_id': self.company_id.security_deposit_account_id.id,
                    'state': 'draft',
                    'name': self.name
                })
            self.create_journal()

            self.write({
                'state': 'done',
                'approver_id': self.env.user.id,
            })

    @api.one
    def toggle_active(self):
        for rec in self:
            super(VendorAgreement, self).toggle_active()
            if not rec.active:
                self.env['vendor.security.deposit'].search([('name', '=', rec.name)]).write({'active': False})
            else:
                self.env['vendor.security.deposit'].search([('name', '=', rec.name),
                                                            ('active', '=', False)]).write({'active': True})

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
        return super(VendorAgreement, self).unlink()

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.product_id:
                name = u'%s[%s]' % (agr.name, agr.product_id.name)
            res.append((agr.id, name))
        return res

    def create_journal(self):
        journal_id = self.env.ref('vendor_agreement.vendor_advance_journal')
        ogl_data = {}
        ogl_data['journal_id'] = journal_id.id
        ogl_data['date'] = fields.date.today()
        ogl_data['operating_unit_id'] = journal_id.operating_unit_id.id
        ogl_data['state'] = 'posted'
        ogl_data['name'] = self.name

        journal_item_data = []
        debit_item = [
            0, 0, {
                'name': self.description or 'Vendor Advance',
                'ref': self.name,
                'date': fields.date.today(),
                'account_id': self.account_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'debit': self.advance_amount,
                'credit': 0.0,
                'due_date': fields.date.today()

            }
        ]
        journal_item_data.append(debit_item)

        if self.type == 'single':
            if self.security_deposit and self.security_deposit > 0:
                deposit_credit_item = [
                    0, 0, {
                        'name': self.description or 'Vendor Advance',
                        'ref': self.name,
                        'date': fields.date.today(),
                        'account_id': self.company_id.security_deposit_account_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'debit': 0.0,
                        'credit': self.security_deposit,
                        'due_date': fields.date.today()

                    }
                ]
                journal_item_data.append(deposit_credit_item)

        supplier_credit_item = [
            0, 0, {
                'name': self.description or 'Vendor Advance',
                'ref': self.name,
                'date': fields.date.today(),
                'account_id': self.partner_id.property_account_payable_id.id,
                'operating_unit_id': journal_id.operating_unit_id.id,
                'debit': 0.0,
                'credit': self.payable_to_supplier,
                'due_date': fields.date.today()

            }
        ]
        journal_item_data.append(supplier_credit_item)
        ogl_data['line_ids'] = journal_item_data

        self.env['account.move'].create(ogl_data)


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    agreement_id = fields.Many2one('agreement', string="Agreement", copy=False)