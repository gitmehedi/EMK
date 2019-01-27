# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True,required=True,
                                        states={'draft': [('readonly',False)]})
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', 'Sub Branch',
                                        readonly=True,states={'draft': [('readonly',False)]})

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        for invoice in self:
            invoice.sub_operating_unit_id = []

    @api.constrains('reference')
    def _check_unique_reference(self):
        if self.partner_id and self.reference:
            filters = [['reference', '=ilike', self.reference.strip()], ['partner_id', '=', self.partner_id.id]]
            bill_no = self.search(filters)
            if len(bill_no) > 1:
                raise UserError(_('Reference must be unique for %s !') % self.partner_id.name)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    operating_unit_id = fields.Many2one('operating.unit',string='Branch',required=True,
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    sub_operating_unit_id = fields.Many2one('sub.operating.unit',string='Sub Branch')

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        for line in self:
            line.sub_operating_unit_id = []
