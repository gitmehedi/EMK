# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Ingredients(models.Model):
    _name = 'gym.ingredient'
    _rec_name = 'no'
    _description = "Gym ingredient"

    no = fields.Char(
        string='No',
        default='New',
        index=True,
        readonly=1,
    )
    name = fields.Char(
        string='Name',
        required = True,
    )
    unit_id = fields.Many2one(
        'product.uom',
         string="Unit of Measure",
    )
    value_in = fields.Char(
        string='Value In',
    )
    energy = fields.Float(
        string='Energy',
    )
    protein = fields.Float(
        string='Protein',
    )
    carbohydrates = fields.Float(
        string='Carbohydrates',
    )
    sugerincarbohydrates = fields.Float(
        string='Suger In Carbohydrates',
    )
    fat = fields.Float(
        string='Fat',
    )
    staturated = fields.Float(
        string='Staturated Fat Content In Fats',
    )
    fibres = fields.Float(
        string='Fibres ',
    )
    sodium = fields.Float(
        string='Sodium',
    )
    ingredient_id = fields.Many2one(
        'gym.nutrition',
        'Nutrition'
    )
    @api.model
    def create(self, vals):
        no = self.env['ir.sequence'].next_by_code('product.add')
        vals.update({
            'no': no
        })
        result = super(Ingredients, self).create(vals)
        return result
