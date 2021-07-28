# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Muscle(models.Model):
    _name = 'gym.muscle'
    _rec_name = 'name'

    no = fields.Char(
        string='No',
        default='New',
        index=True,
        readonly=1,
    )
    name = fields.Char(string='Name')
    description = fields.Text(
        string='Description',
    )
    image = fields.Binary(
        string='Image',
        store=True,
    )
    typeside = fields.Selection([
        ('front_side', 'Front Side'),
        ('back_side', 'Back Side')],
        string='Type',
    )
    exercise_category_id = fields.Many2many(
        'exercise.category.select',
        string='Exercise Category'
    )

    @api.model
    def create(self, vals):
        no = self.env['ir.sequence'].next_by_code('gym.muscle')
        vals.update({
            'no': no
        })
        result = super(Muscle, self).create(vals)
        return result
