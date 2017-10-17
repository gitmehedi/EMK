from odoo import models, fields, api


class BDDistrict(models.Model):
    _name = 'bd.district'

    name = fields.Char(string='District Name')