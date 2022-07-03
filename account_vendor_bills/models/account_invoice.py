from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']

    amount_payable = fields.Float('Vendor Payable', readonly=True, copy=False, compute='_compute_amount_payable')


    # @api.depends('invoice_line_ids', 'tax_line_ids')
    # def _compute_amount_payable(self):
    #     for inv in self:
    #         payable = 0
    #         self.env.context = dict(self.env.context)
    #         self.env.context.update({
    #             'noonchange': True,
    #         })
    #         # counting invoice line amount
    #         for inv_line in inv.invoice_line_ids:
    #             price = inv_line.price_subtotal
    #             for tax in inv_line.invoice_line_tax_ids:
    #                 if len(tax.children_tax_ids) > 0:
    #                     for ctax in tax.children_tax_ids:
    #                         # considering include in expense
    #                         if ctax.include_in_expense:
    #                             if ctax.is_vat:
    #                                 price += inv_line.price_tax
    #                             else:
    #                                 price += inv_line.price_tds
    #                 else:
    #                     if tax.include_in_expense:
    #                         if tax.is_vat:
    #                             price += inv_line.price_tax
    #                         else:
    #                             price += inv_line.price_tds
    #             payable += price
    #
    #         # considering if the vat or tax rules are reverse
    #         for tax_line in inv.tax_line_ids:
    #             if tax_line.tax_id.is_reverse:
    #                 payable -= round(tax_line.amount, 2)
    #             else:
    #                 payable += round(tax_line.amount, 2)
    #
    #
    #
    #         # considering adjustable vat and tds
    #         if inv.adjustable_vat > 0 or inv.adjustable_tds > 0:
    #             payable += inv.adjustable_vat
    #             payable += inv.adjustable_tds
    #
    #         # considering security deposit
    #         if inv.security_deposit > 0:
    #             payable -= inv.security_deposit
    #
    #         if payable < 0:
    #             payable = 0.00
    #
    #         inv.amount_payable = payable
    #
    # @api.model
    # def create(self, vals):
    #     if vals.get('reference'):
    #         vals['reference'] = vals['reference'].strip()
    #     return super(AccountInvoice, self).create(vals)
    #
    # @api.multi
    # def write(self, vals):
    #     if all(rec.state == 'draft' for rec in self):
    #         if vals.get('reference'):
    #             vals.update({'reference': vals.get('reference').strip()})
    #         return super(AccountInvoice, self).write(vals)
    #
    # @api.model
    # def _needaction_domain_get(self):
    #     return [('state', 'in', ('open', 'draft'))]
    #
    # @api.model
    # def invoice_line_move_line_get(self):
    #     res = super(AccountInvoice, self).invoice_line_move_line_get()
    #     if res:
    #         for iml in res:
    #             inv_line_obj = self.env['account.invoice.line'].search([('id', '=', iml['invl_id'])])
    #             iml.update({'operating_unit_id': inv_line_obj.operating_unit_id.id,
    #                         'sub_operating_unit_id': inv_line_obj.sub_operating_unit_id.id})
    #     return res
    #
    #
    #
    # # @api.multi
    # # def finalize_invoice_move_lines(self, move_lines):
    # #     move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
    # #     count = 1
    # #     for line in move_lines:
    # #         val = line[2]
    # #         if val['account_id'] == self.partner_id.property_account_payable_id.id:
    # #             val_ou = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
    # #             # val['operating_unit_id'] = self.invoice_line_ids[0].operating_unit_id.id or False
    # #             val['operating_unit_id'] = val_ou.id or False
    # #             if self.partner_id.property_account_payable_sou_id:
    # #                 val['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
    # #             else:
    # #                 raise ValidationError(
    # #                     "[Configuration Error] Please configure Sequence for the following Vendor: \n {}".format(
    # #                         self.partner_id.name))
    # #             val['reconcile_ref'] = self.get_reconcile_ref(self.account_id.id, self.id)
    # #
    # #         elif 'product_id' in val and val['product_id'] > 0:
    # #             val['reconcile_ref'] = self.get_reconcile_ref(val['account_id'], str(self.id) + str(count))
    # #             count = count + 1
    # #
    # #     return move_lines
    #
    # @api.multi
    # def action_move_create(self):
    #     res = super(AccountInvoice, self).action_move_create()
    #     if res:
    #         for inv in self:
    #             move = self.env['account.move'].browse(inv.move_id.id)
    #             for line in move.line_ids:
    #                 if line.advance_id:
    #                     line.write({'sub_operating_unit_id': line.advance_id.sub_operating_unit_id.id or False,
    #                                 'analytic_account_id': line.advance_id.account_analytic_id.id or False})
    #                 if line.is_security_deposit:
    #                     if self.env.user.company_id.security_deposit_sequence_id:
    #                         line.write(
    #                             {
    #                                 'sub_operating_unit_id': self.env.user.company_id.security_deposit_sequence_id.id or False}
    #                         )
    #                     else:
    #                         raise ValidationError("[Configuration Error] Please configure security deposit sequence in "
    #                                               "Accounting Configuration")
    #
    #             move.write({
    #                 'maker_id': self.user_id.id,
    #                 'approver_id': self.env.user.id
    #             })
    #
    #     return res
    #
    # def create_security_deposit(self):
    #     res = super(AccountInvoice, self).create_security_deposit()
    #     res.write({'sub_operating_unit_id': self.env.user.company_id.security_deposit_sequence_id.id or False})
    #     return res
    #
    # # this function is required to pass the reconcile reference in security deposit move line
    # def get_security_deposit_move_data(self):
    #     res = super(AccountInvoice, self).get_security_deposit_move_data()
    #     if self.company_id.security_deposit_account_id:
    #         res['reconcile_ref'] = self.get_reconcile_ref(self.company_id.security_deposit_account_id.id, self.id)
    #         res['name'] = self.invoice_line_ids[0].name or 'Security Deposit'
    #     return res
    #
    # # this function is required to pass the reconcile reference in adjusted advance move line
    # def get_advance_line_item(self, advance):
    #     res = super(AccountInvoice, self).get_advance_line_item(advance)
    #     res['reconcile_ref'] = advance.reconcile_ref
    #     return res
    #
    # # this function is required to pass the reconcile reference in vendor security deposit
    # def get_security_deposit_data(self):
    #     res = super(AccountInvoice, self).get_security_deposit_data()
    #     if self.company_id.security_deposit_account_id:
    #         res['reconcile_ref'] = self.get_reconcile_ref(self.company_id.security_deposit_account_id.id, self.id)
    #     return res
    #
    # def get_reconcile_ref(self, account_id, ref):
    #     # Generate reconcile ref code
    #     reconcile_ref = None
    #     account_obj = self.env['account.account'].search([('id', '=', account_id)])
    #     if account_obj.reconcile:
    #         reconcile_ref = account_obj.code + 'VB' + str(ref)
    #
    #     return reconcile_ref


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    name = fields.Char(string='Narration', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cost Centre', required=True)

    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True, readonly=False,
                                        default=lambda self: self.env['res.users'].operating_unit_default_get(
                                            self._uid), related='')
