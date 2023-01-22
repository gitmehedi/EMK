# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True,
                                        states={'draft': [('readonly',
                                                           False)]})

    # @api.multi
    # def finalize_invoice_move_lines(self, move_lines):
    #     move_lines = super(AccountInvoice,
    #                        self).finalize_invoice_move_lines(move_lines)
    #     new_move_lines = []
    #     for line_tuple in move_lines:
    #         if self.operating_unit_id:
    #             line_tuple[2]['operating_unit_id'] = \
    #                 self.operating_unit_id.id
    #         new_move_lines.append(line_tuple)
    #     return new_move_lines



class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    operating_unit_id = fields.Many2one('operating.unit',
                                        related='invoice_id.operating_unit_id',
                                        string='Operating Unit', store=True,
                                        readonly=True)
