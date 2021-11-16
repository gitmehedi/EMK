from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorAdvance(models.Model):
    _name = 'vendor.advance'
    _inherit = ['vendor.advance', 'ir.needaction_mixin']

    reconcile_ref = fields.Char(string="Reconciliation Ref#", size=20)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', required=True,
                                            track_visibility='onchange', readonly=True,
                                            states={'draft': [('readonly', False)]})

    operating_unit_domain_ids = fields.Many2many('operating.unit', compute="_compute_operating_unit_domain_ids",
                                                 readonly=True, store=False)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cost Centre',
                                          readonly=True, required='True', track_visibility='onchange',
                                          states={'draft': [('readonly', False)]})
    payment_type = fields.Selection([('casa', 'CASA'), ('credit', 'Credit Account')], default='casa',
                                    string='Payment To', readonly=True, states={'draft': [('readonly', False)]},
                                    track_visibility='onchange', required=True)
    vendor_bank_acc = fields.Char(string='Vendor Bank Account', related='partner_id.vendor_bank_acc', size=13,
                                  readonly=True, track_visibility='onchange')
    credit_account_id = fields.Many2one('account.account', string='Credit Account', track_visibility='onchange',
                                        readonly=True, states={'draft': [('readonly', False)]})
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence',
                                                   track_visibility='onchange', readonly=True,
                                                   states={'draft': [('readonly', False)]})
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch', track_visibility='onchange',
                                               readonly=True, states={'draft': [('readonly', False)]})
    credit_operating_unit_domain_ids = fields.Many2many('operating.unit', readonly=True, store=False,
                                                        compute="_compute_credit_operating_unit_domain_ids")
    date = fields.Date(string='Date ', required=True, default=lambda self: self.env.user.company_id.batch_date,
                       track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    @api.depends('sub_operating_unit_id')
    def _compute_operating_unit_domain_ids(self):
        for rec in self:
            if rec.sub_operating_unit_id.all_branch:
                rec.operating_unit_domain_ids = self.env['operating.unit'].search([])
            else:
                rec.operating_unit_domain_ids = rec.sub_operating_unit_id.branch_ids

    @api.multi
    @api.depends('credit_sub_operating_unit_id')
    def _compute_credit_operating_unit_domain_ids(self):
        for rec in self:
            if rec.credit_sub_operating_unit_id.all_branch:
                rec.credit_operating_unit_domain_ids = self.env['operating.unit'].search([])
            else:
                rec.credit_operating_unit_domain_ids = rec.credit_sub_operating_unit_id.branch_ids

    @api.onchange('sub_operating_unit_id')
    def _onchange_sub_operating_unit_id(self):
        for rec in self:
            rec.operating_unit_id = None

    @api.onchange('account_id')
    def _onchange_account_id(self):
        for rec in self:
            rec._check_valid_gl_account()
            rec.sub_operating_unit_id = None

    def get_debit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_debit_item_data(journal_id)
        res['sub_operating_unit_id'] = self.sub_operating_unit_id.id or False
        res['analytic_account_id'] = self.account_analytic_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        self.reconcile_ref = res['reconcile_ref']
        return res

    def get_deposit_credit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_deposit_credit_item_data(journal_id)
        res['sub_operating_unit_id'] = self.company_id.security_deposit_sequence_id.id or False
        res['analytic_account_id'] = self.account_analytic_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def get_vat_item_data(self, vat_id, vat_amount):
        res = super(VendorAdvance, self).get_vat_item_data(vat_id, vat_amount)
        res['sub_operating_unit_id'] = vat_id.sou_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def get_tds_item_data(self, tds_id, tds_amount):
        res = super(VendorAdvance, self).get_tds_item_data(tds_id, tds_amount)
        res['sub_operating_unit_id'] = tds_id.sou_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def get_supplier_credit_item_data(self, journal_id, supplier_credit_amount):
        # this function will trigger at the approval of vendor advance/rent agreement
        res = super(VendorAdvance, self).get_supplier_credit_item_data(journal_id, supplier_credit_amount)
        op_unit = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
        res['operating_unit_id'] = op_unit.id or False
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def _get_debit_line_for_amendment(self, amount):
        res = super(VendorAdvance, self)._get_debit_line_for_amendment(amount)
        res['operating_unit_id'] = self.operating_unit_id.id or False
        res['sub_operating_unit_id'] = self.sub_operating_unit_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        res['date'] = self.env.user.company_id.batch_date or fields.Date.today()
        return res

    def _get_credit_line_for_amendment(self, amount):
        res = super(VendorAdvance, self)._get_credit_line_for_amendment(amount)
        op_unit = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
        res['operating_unit_id'] = op_unit.id or False
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        res['date'] = self.env.user.company_id.batch_date or fields.Date.today()
        ref = res['ref']
        if len(self.move_ids) >= 1:
            ref += str(len(self.move_ids))
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], ref)
        return res

    def create_journal(self, journal_id):
        move = super(VendorAdvance, self).create_journal(journal_id)
        move.write({
            'maker_id': self.maker_id.id,
            'approver_id': self.env.user.id
        })
        return move

    def create_journal_for_amendment(self, amount, journal_id):
        move = super(VendorAdvance, self).create_journal_for_amendment(amount, journal_id)
        move.write({
            'date': self.env.user.company_id.batch_date or fields.Date.today(),
            'maker_id': self.maker_id.id,
            'approver_id': self.env.user.id
        })
        return move

    def create_security_deposit(self):
        res = super(VendorAdvance, self).create_security_deposit()
        if res:
            res.write({'sub_operating_unit_id': self.company_id.security_deposit_sequence_id.id})
        return res

    def get_reconcile_ref(self, account_id, ref):
        # Generate reconcile ref code
        reconcile_ref = None
        account_obj = self.env['account.account'].search([('id', '=', account_id)])
        if account_obj.reconcile:
            reconcile_ref = account_obj.code + ref.replace('/', '')
            if len(reconcile_ref) > 20:
                reconcile_ref = reconcile_ref.replace('A', '')

        return reconcile_ref

    def get_security_deposit_data(self):
        res = super(VendorAdvance, self).get_security_deposit_data()
        if self.company_id.security_deposit_account_id:
            res['reconcile_ref'] = self.get_reconcile_ref(self.company_id.security_deposit_account_id.id, self.name)
        return res

    @api.constrains('account_id', 'type')
    def check_account_id(self):
        self._check_valid_gl_account()

    def _check_valid_gl_account(self):
        if self.type == 'multi' and self.account_id:
            if self.account_id.reconcile or self.account_id.originating_type == 'credit':
                raise ValidationError("[Validation Error] Please select the appropiate GL Account")

    @api.multi
    def action_approve_amendment(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.is_amendment == True:
            requested = self.history_line_ids.search([('state', '=', 'pending'),
                                                      ('rent_id', '=', self.id)],
                                                     order='id desc', limit=1)
            if requested:
                rec = {}
                if requested.end_date:
                    rec['end_date'] = requested.end_date
                if 'additional_advance_amount' in requested:
                    rec['additional_advance_amount'] = self.additional_advance_amount + requested.advance_amount_add
                if requested.adjustment_value:
                    rec['adjustment_value'] = requested.adjustment_value
                if requested.area:
                    rec['area'] = requested.area
                if requested.rate:
                    rec['rate'] = requested.rate
                if requested.service_value:
                    rec['service_value'] = requested.service_value
                if requested.account_id:
                    rec['account_id'] = requested.account_id.id
                rec['is_amendment'] = False
                rec['active'] = True
                if requested.state:
                    rec['state'] = 'inactive' if not requested.active_status else 'approve'
                if requested.vat_id:
                    rec['vat_id'] = requested.vat_id.id
                if requested.tds_id:
                    rec['tds_id'] = requested.tds_id.id
                if requested.payment_type:
                    rec['payment_type'] = requested.payment_type
                if requested.vendor_bank_acc:
                    rec['vendor_bank_acc'] = requested.vendor_bank_acc
                if requested.credit_account_id:
                    rec['credit_account_id'] = requested.credit_account_id.id
                if requested.credit_sub_operating_unit_id:
                    rec['credit_sub_operating_unit_id'] = requested.credit_sub_operating_unit_id.id
                if requested.credit_operating_unit_id:
                    rec['credit_operating_unit_id'] = requested.credit_operating_unit_id.id
                if requested.additional_service_value:
                    rec['additional_service_value'] = requested.additional_service_value
                if requested.billing_period:
                    rec['billing_period'] = requested.billing_period

                self.write(rec)
                amount = requested.advance_amount_add
                if amount > 0:
                    journal_type = self.env.ref('vendor_advance.vendor_advance_journal')
                    self.create_journal_for_amendment(amount, journal_type)
                requested.write({'state': 'confirm'})


class InheritAgreementHistory(models.Model):
    _inherit = "agreement.history"

    vat_id = fields.Many2one('account.tax', string='VAT', domain=[('is_vat', '=', True)])
    tds_id = fields.Many2one('account.tax', string='TDS', domain=[('is_tds', '=', True)])
    payment_type = fields.Selection([('casa', 'CASA'), ('credit', 'Credit Account')], string='Payment To')
    vendor_bank_acc = fields.Char(string='Vendor Bank Account', size=13, track_visibility='onchange')
    credit_account_id = fields.Many2one('account.account', string='Credit Account')
    credit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Credit Sequence')
    credit_operating_unit_id = fields.Many2one('operating.unit', string='Credit Branch')
    additional_service_value = fields.Float(string="Ad. Service Value")
    billing_period = fields.Selection([('monthly', "Monthly"), ('yearly', "Yearly")])
