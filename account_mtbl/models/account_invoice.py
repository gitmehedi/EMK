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

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        for line in move_lines:
            if line[2]['name'] == '/':
                line[2]['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False

        return move_lines

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        if res:
            for inv in self:
                move = self.env['account.move'].browse(inv.move_id.id)
                for line in move.line_ids:
                    if line.product_id:
                        for inv_line in inv.invoice_line_ids:
                            if inv_line.product_id.id == line.product_id.id:
                                line.write({'sub_operating_unit_id': inv_line.sub_operating_unit_id.id})
                    if line.tax_line_id:
                        line.write({'sub_operating_unit_id': line.tax_line_id.sou_id.id or False})
                    if line.advance_id:
                        line.write({'sub_operating_unit_id': line.advance_id.sub_operating_unit_id.id or False})

        return res


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






