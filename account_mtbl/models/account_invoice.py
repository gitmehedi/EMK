from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']


    @api.model
    def create(self, vals):
        if vals.get('reference'):
            vals['reference'] = vals['reference'].strip()
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.state == 'draft':
            if vals.get('reference'):
                vals.update({'reference': vals.get('reference').strip()})
            return super(AccountInvoice, self).write(vals)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

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
            r['operating_unit_id'] = tax.operating_unit_id.id
            r['sub_operating_unit_id'] = tax.sou_id.id
            new_res.append(r)
        return new_res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        for line in move_lines:
            if line[2]['name'] == '/':
                line[2]['operating_unit_id'] = self.invoice_line_ids[0].operating_unit_id.id or False
                line[2]['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
                line[2]['reconcile_ref'] = self.get_reconcile_ref(self.account_id.id, self.id)  # setting the reconcile ref

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
                        line.write(
                            {'sub_operating_unit_id': self.env.user.company_id.security_deposit_sequence_id.id or False}
                        )

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

    @api.onchange('account_id')
    def _onchange_account_id(self):
        for rec in self:
            rec.sub_operating_unit_id = None


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






