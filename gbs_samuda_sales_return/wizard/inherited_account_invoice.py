# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(InheritedAccountInvoice, self)._prepare_refund(invoice, date_invoice=date_invoice,
                                                                      date=date,
                                                                      description=description,
                                                                      journal_id=journal_id)

        values.update({'cost_center_id': invoice.cost_center_id.id or False, 'lc_id': invoice.lc_id.id or False, 'payment_term_id': invoice.payment_term_id.id or False, 'pack_type': invoice.pack_type.id or False, 'currency_id': invoice.currency_id.id or False, 'sale_type_id': invoice.sale_type_id.id or False})
        return values
