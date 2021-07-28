# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Nutrition(models.Model):
    _name = 'gym.nutrition'
    _rec_name = 'customer_id'

    no = fields.Char(
        string='No',
        default='New',
        index=True,
        readonly=1,
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )
    nutrition_ids = fields.Many2many(
        'gym.ingredient',
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Datetime.now,
    )

    @api.model
    def create(self, vals):
        no = self.env['ir.sequence'].next_by_code('gym.nutrition')
        vals.update({
            'no': no
        })
        result = super(Nutrition, self).create(vals)
        return result

