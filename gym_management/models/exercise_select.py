# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExerciseSelect(models.Model):
    _name = 'exercise.select'
    _rec_name = 'name'

    name = fields.Char(
        string='Name',
        required = True
    )

    @api.model
    def create(self, vals):
        no = self.env['ir.sequence'].next_by_code('exercise.select')
        vals.update({
            'no': no
        })
        result = super(ExerciseSelect, self).create(vals)
        return result
