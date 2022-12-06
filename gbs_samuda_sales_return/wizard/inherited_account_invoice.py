# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        if self.invoice_line_ids and self.type == 'out_refund':
            for line in self.invoice_line_ids:
                if line.account_id.user_type_id.name == 'Income':
                    self.from_return = True
                elif line.account_id.user_type_id.name == 'Expenses':
                    self.from_return = False
                else:
                    raise UserError(
                        _("Refund Invoice GL type must be either expense or income!"))

        res = super(InheritedAccountInvoice, self).action_invoice_open()

        return res


    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(InheritedAccountInvoice, self)._prepare_refund(invoice, date_invoice=date_invoice,
                                                                      date=date,
                                                                      description=description,
                                                                      journal_id=journal_id)
        values.update({'cost_center_id': invoice.cost_center_id.id or False, 'lc_id': invoice.lc_id.id or False,
                       'payment_term_id': invoice.payment_term_id.id or False,
                       'pack_type': invoice.pack_type.id or False, 'currency_id': invoice.currency_id.id or False,
                       'conversion_rate': invoice.conversion_rate, 'sale_type_id': invoice.sale_type_id.id or False,
                       'so_id': invoice.so_id.id or False})
        return values


class InheritedAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    auto_refunded_qty = fields.Float(default=0.0)

    # @api.onchange('account_id')
    # def _onchange_account_id(self):
    #     invoice_id = self._origin.invoice_id.id
    #     if not invoice_id:
    #         raise UserError(
    #             _("You cannot change GL! Contact Administrator!"))
    #
    #     if not isinstance(invoice_id, int):
    #         raise UserError(
    #             _("You cannot change GL! Contact Administrator!"))
    #
    #     print('self.account', self.account_id)
    #     invoice_obj = self.env['account.invoice'].browse(invoice_id)
    #
    #     #invoice_obj.sudo().write({'from_return': True})
    #
    #     return super(InheritedAccountInvoiceLine, self)._onchange_account_id()



