# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Bim(models.Model):
    _name = 'gym.bim'
    _rec_name = 'height'
    _description = "Gym ingredient"

    height = fields.Float(
        default=1.75,
        string='Height',
        required = True,
    )
    weight = fields.Float(
        default=70,
        string='Weight',
        required = True,
    )
    bmi = fields.Float(
        string='Bmi',
        default=0.0,
        compute='_compute_bmi',
    )

    @api.multi
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for rec in self:
            rec.bmi = rec.weight / (rec.height * rec.height)
