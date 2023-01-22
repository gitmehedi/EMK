from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']
    amount_payable = fields.Float('Vendor Payable', readonly=True, copy=False, compute='_compute_amount_payable')

    def _get_date_invoice(self):
        return self.env.user.company_id.batch_date

    date_invoice = fields.Date(default=_get_date_invoice, required=True)

    @api.depends('adjusted_advance', 'invoice_line_ids', 'tax_line_ids', 'adjustable_vat', 'adjustable_tds',
                 'security_deposit')
    def _compute_amount_payable(self):
        for inv in self:
            payable = 0
            self.env.context = dict(self.env.context)
            self.env.context.update({
                'noonchange': True,
            })
            # counting invoice line amount
            for inv_line in inv.invoice_line_ids:
                price = inv_line.price_subtotal
                for tax in inv_line.invoice_line_tax_ids:
                    if len(tax.children_tax_ids) > 0:
                        for ctax in tax.children_tax_ids:
                            # considering include in expense
                            if ctax.include_in_expense:
                                if ctax.is_vat:
                                    price += inv_line.price_tax
                                else:
                                    price += inv_line.price_tds
                    else:
                        if tax.include_in_expense:
                            if tax.is_vat:
                                price += inv_line.price_tax
                            else:
                                price += inv_line.price_tds
                payable += price

            # considering if the vat or tax rules are reverse
            for tax_line in inv.tax_line_ids:
                if tax_line.tax_id.is_reverse:
                    payable -= round(tax_line.amount, 2)
                else:
                    payable += round(tax_line.amount, 2)

            # considering adjusted advance amount
            if inv.adjusted_advance > 0:
                payable -= inv.adjusted_advance

            # considering adjustable vat and tds
            if inv.adjustable_vat > 0 or inv.adjustable_tds > 0:
                payable += inv.adjustable_vat
                payable += inv.adjustable_tds

            # considering security deposit
            if inv.security_deposit > 0:
                payable -= inv.security_deposit

            if payable < 0:
                payable = 0.00

            inv.amount_payable = payable

    @api.model
    def create(self, vals):
        if vals.get('reference'):
            vals['reference'] = vals['reference'].strip()
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if all(rec.state == 'draft' for rec in self):
            if vals.get('reference'):
                vals.update({'reference': vals.get('reference').strip()})
            return super(AccountInvoice, self).write(vals)

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('open', 'draft'))]

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        if res:
            for iml in res:
                inv_line_obj = self.env['account.invoice.line'].search([('id', '=', iml['invl_id'])])
                iml.update({'operating_unit_id': inv_line_obj.operating_unit_id.id,
                            'sub_operating_unit_id': inv_line_obj.sub_operating_unit_id.id})
        return res

    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()
        tax_pool = self.env['account.tax']
        new_res = []
        for r in res:
            tax = tax_pool.search([('id', '=', r['tax_line_id'])])[0]
            if tax.is_vat:
                tax_type = 'VAT'
            elif tax.is_tds:
                tax_type = 'TDS'
            if tax.operating_unit_id:
                r['operating_unit_id'] = tax.operating_unit_id.id
            else:
                r['operating_unit_id'] = self.invoice_line_ids[0].operating_unit_id.id
            if tax.sou_id:
                r['sub_operating_unit_id'] = tax.sou_id.id
            else:
                raise ValidationError(
                    "[Configuration Error] Please configure Sequence for the following {} rule: \n {}".format(tax_type,
                                                                                                              tax.name))
            product = self.tax_line_ids.search([('id', '=', r['invoice_tax_line_id'])])
            r['product_id'] = product.product_id.id if product else None
            new_res.append(r)
        return new_res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        count = 1
        for line in move_lines:
            val = line[2]
            if val['account_id'] == self.partner_id.property_account_payable_id.id:
                val_ou = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
                # val['operating_unit_id'] = self.invoice_line_ids[0].operating_unit_id.id or False
                val['operating_unit_id'] = val_ou.id or False
                if self.partner_id.property_account_payable_sou_id:
                    val['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
                else:
                    raise ValidationError(
                        "[Configuration Error] Please configure Sequence for the following Vendor: \n {}".format(
                            self.partner_id.name))
                val['reconcile_ref'] = self.get_reconcile_ref(self.account_id.id, self.id)

            elif 'product_id' in val and val['product_id'] > 0:
                val['reconcile_ref'] = self.get_reconcile_ref(val['account_id'], str(self.id) + str(count))
                count = count + 1

        return move_lines

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        if res:
            for inv in self:
                move = self.env['account.move'].browse(inv.move_id.id)
                for line in move.line_ids:
                    if line.advance_id:
                        line.write({'sub_operating_unit_id': line.advance_id.sub_operating_unit_id.id or False,
                                    'analytic_account_id': line.advance_id.account_analytic_id.id or False})
                    if line.is_security_deposit:
                        if self.env.user.company_id.security_deposit_sequence_id:
                            line.write(
                                {
                                    'sub_operating_unit_id': self.env.user.company_id.security_deposit_sequence_id.id or False}
                            )
                        else:
                            raise ValidationError("[Configuration Error] Please configure security deposit sequence in "
                                                  "Accounting Configuration")

                move.write({
                    'maker_id': self.user_id.id,
                    'approver_id': self.env.user.id
                })

        return res

    def create_security_deposit(self):
        res = super(AccountInvoice, self).create_security_deposit()
        res.write({'sub_operating_unit_id': self.env.user.company_id.security_deposit_sequence_id.id or False})
        return res

    # this function is required to pass the reconcile reference in security deposit move line
    def get_security_deposit_move_data(self):
        res = super(AccountInvoice, self).get_security_deposit_move_data()
        if self.company_id.security_deposit_account_id:
            res['reconcile_ref'] = self.get_reconcile_ref(self.company_id.security_deposit_account_id.id, self.id)
            res['name'] = self.invoice_line_ids[0].name or 'Security Deposit'
        return res

    # this function is required to pass the reconcile reference in adjusted advance move line
    def get_advance_line_item(self, advance):
        res = super(AccountInvoice, self).get_advance_line_item(advance)
        res['reconcile_ref'] = advance.reconcile_ref
        return res

    # this function is required to pass the reconcile reference in vendor security deposit
    def get_security_deposit_data(self):
        res = super(AccountInvoice, self).get_security_deposit_data()
        if self.company_id.security_deposit_account_id:
            res['reconcile_ref'] = self.get_reconcile_ref(self.company_id.security_deposit_account_id.id, self.id)
        return res

    def get_reconcile_ref(self, account_id, ref):
        # Generate reconcile ref code
        reconcile_ref = None
        account_obj = self.env['account.account'].search([('id', '=', account_id)])
        if account_obj.reconcile:
            reconcile_ref = account_obj.code + 'VB' + str(ref)

        return reconcile_ref


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    name = fields.Char(string='Narration', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cost Centre', required=True)

    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True, readonly=False,
                                        default=lambda self: self.env['res.users'].operating_unit_default_get(
                                            self._uid), related='')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', required=True)

    operating_unit_domain_ids = fields.Many2many('operating.unit', compute="_compute_operating_unit_domain_ids",
                                                 readonly=True, store=False)

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

    @api.constrains('quantity')
    def _check_quantity(self):
        if self.quantity < 1:
            raise ValidationError('Quantity can not be less than 1.00')

    @api.constrains('price_unit')
    def _check_unit_price(self):
        if self.price_unit <= 0:
            raise ValidationError('Unit Price can not be equal or less than Zero(0)')


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        res = super(ProductProduct, self)._convert_prepared_anglosaxon_line(line, partner)
        if res:
            if line.get('operating_unit_id'):
                res.update({'operating_unit_id': line.get('operating_unit_id')})
            if line.get('sub_operating_unit_id'):
                res.update({'sub_operating_unit_id': line.get('sub_operating_unit_id')})
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    product_id = fields.Many2one('product.product', string='Product', required=True)
