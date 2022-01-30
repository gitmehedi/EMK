from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']
    amount_payable = fields.Float('Vendor Payable', readonly=True, copy=False)

    def _get_date_invoice(self):
        return self.env.user.company_id.batch_date

    # date_invoice = fields.Date(default=_get_date_invoice, required=True)
    date_invoice = fields.Date()

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
                iml.update({'operating_unit_id': inv_line_obj.operating_unit_id.id})
        return res

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        if res:
            for inv in self:
                move = self.env['account.move'].browse(inv.move_id.id)
                move.write({
                    'maker_id': self.user_id.id,
                    'approver_id': self.env.user.id
                })

        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    name = fields.Char(string='Narration', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cost Centre')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True, readonly=False,
                                        default=lambda self: self.env['res.users'].operating_unit_default_get(
                                            self._uid), related='')

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
