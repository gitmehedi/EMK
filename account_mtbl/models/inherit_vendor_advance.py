from odoo import models, fields, api
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
        return res

    def _get_credit_line_for_amendment(self, amount):
        res = super(VendorAdvance, self)._get_credit_line_for_amendment(amount)
        op_unit = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
        res['operating_unit_id'] = op_unit.id or False
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        ref = res['ref']
        if len(self.move_ids) >= 1:
            ref += str(len(self.move_ids))
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], ref)
        return res

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
    def check_security_deposit(self):
        self._check_valid_gl_account()

    def _check_valid_gl_account(self):
        if self.type == 'multi' and self.account_id:
            if self. account_id.reconcile or self.account_id.originating_type == 'credit':
                raise ValidationError("[Validation Error] Please select the appropiate GL Account")


