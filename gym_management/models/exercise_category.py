# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExerciseCategory(models.Model):
    _name = 'exercise.category'
    _rec_name = 'exercise_category_id'

    no = fields.Char(
        string='No Reference',
        default='New',
        index=True,
        readonly=1,
    )
    category = fields.Selection([
        ('acehold', 'Axe Hold'),
        ('barbell tricep extension', 'Barbell Tricep Extension')],
        string='Exercise',
    )
    name = fields.Char(
        string='Select Your Exercise',
    )
    description = fields.Text(
        string='Description',
    )
    muscles_id = fields.Many2one(
        'gym.muscle',
        string='Affected Muscles',
    )
    equipment_id = fields.Many2one(
        'product.product',
        string='Equipment',
    )
    image = fields.Binary(
        string='Image',
    )
    exercise_id = fields.Many2one(
        'exercise.select',
        string='Exercise On',
    )
    exercise_category_id = fields.Many2one(
        'exercise.category.select',
        string='Exercise',
    )

    @api.model
    def create(self, vals):
        no = self.env['ir.sequence'].next_by_code('exercise.category')
        vals.update({
            'no': no
        })
        result = super(ExerciseCategory, self).create(vals)
        return result
