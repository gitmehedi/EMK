# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PaymentSession(models.Model):
    _inherit = 'payment.session'

    member_fee_ids = fields.One2many('invoice.payment', 'session_id', domain=[('state', 'in', ['draft', 'paid'])],
                                     string='Membership Fee', track_visibility="onchange")
    service_fee_ids = fields.One2many('service.payment', 'session_id', domain=[('state', 'in', ['draft', 'paid'])],
                                      string='Service Fee', track_visibility="onchange")
    total_amount = fields.Float(compute="_compute_total_amount")

    @api.depends('member_fee_ids', 'service_fee_ids')
    def _compute_total_amount(self):
        for rec in self:
            mem_coll = sum([val.paid_amount for val in rec.member_fee_ids])
            ser_coll = sum([val.paid_amount for val in rec.service_fee_ids])
            rec.total_amount = mem_coll + ser_coll
