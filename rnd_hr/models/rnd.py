from odoo import api, fields, models, _

class RnD(models.Model):

    _name = 'rnd.rostering'


    name = fields.Char(string='Number')
