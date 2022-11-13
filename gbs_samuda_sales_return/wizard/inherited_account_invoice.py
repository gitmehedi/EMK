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

        values.update({'cost_center_id': invoice.cost_center_id.id or False, 'lc_id': invoice.lc_id.id or False})
        return values
