# -*- coding: utf-8 -*-

from odoo import models, api, fields,_
from odoo.addons.opa_utility.helper.utility import Message
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


class PosCategory(models.Model):
    _name = "pos.category"
    _inherit = ['pos.category', 'mail.thread', 'ir.needaction_mixin']

    status = fields.Boolean(string='Status', default=True, track_visibility="onchange")
    name = fields.Char(required=True, translate=True, track_visibility="onchange")
    parent_id = fields.Many2one('pos.category', track_visibility="onchange")
    child_id = fields.One2many('pos.category', 'parent_id', track_visibility="onchange")
    sequence = fields.Integer(track_visibility="onchange")
    image = fields.Binary(track_visibility="onchange")
    image_medium = fields.Binary(track_visibility="onchange")
    image_small = fields.Binary(track_visibility="onchange")

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', True)]

    @api.multi
    def unlink(self):
        for rec in self:
            products = self.env['product.product'].search([('pos_categ_id', '=', rec.id)])
            if len(products) > 0:
                raise ValidationError(_(Message.UNLINK_WARNING))
            try:
                super(PosCategory, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))
