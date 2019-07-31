# -*- coding: utf-8 -*-

import random

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_asset = fields.Boolean(default=False)

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        res = super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)
        if res:
            if True in [i.is_asset for i in self]:
                self.browse(res).write({'is_asset':True})
        return res
