from odoo import models, fields, api, _


class VendorAdvance(models.Model):
    _name = 'vendor.advance'
    _inherit = ['vendor.advance', 'ir.needaction_mixin']

    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', required=True,
                                            track_visibility='onchange', readonly=True,
                                            states={'draft': [('readonly', False)]})

    operating_unit_domain_ids = fields.Many2many('operating.unit', compute="_compute_operating_unit_domain_ids", readonly=True, store=False)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cost Centre',
                                          readonly=True, required='True', track_visibility='onchange',
                                          states={'draft': [('readonly', False)]})

    @api.multi
    @api.depends('sub_operating_unit_id')
    def _compute_operating_unit_domain_ids(self):
        for rec in self:
            if rec.sub_operating_unit_id.all_branch:
                rec.operating_unit_domain_ids = self.env['operating.unit'].search([])
            else:
                rec.operating_unit_domain_ids = rec.sub_operating_unit_id.branch_ids

    @api.onchange('sub_operating_unit_id')
    def _onchange_sub_operating_unit_id(self):
        for rec in self:
            rec.operating_unit_id = None

    @api.onchange('account_id')
    def _onchange_account_id(self):
        for rec in self:
            rec.sub_operating_unit_id = None

    def get_debit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_debit_item_data(journal_id)
        res['sub_operating_unit_id'] = self.sub_operating_unit_id.id or False
        res['analytic_account_id'] = self.account_analytic_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
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
        res = super(VendorAdvance, self).get_supplier_credit_item_data(journal_id, supplier_credit_amount)
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def _get_debit_line_for_amendment(self, amount):
        res = super(VendorAdvance, self)._get_debit_line_for_amendment(amount)
        res['sub_operating_unit_id'] = self.sub_operating_unit_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def _get_credit_line_for_amendment(self, amount):
        res = super(VendorAdvance, self)._get_credit_line_for_amendment(amount)
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
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

        return reconcile_ref

