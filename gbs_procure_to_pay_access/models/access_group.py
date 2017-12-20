from openerp import fields, models



class AccessGroup(models.Model):
    _inherit = ['res.groups']

    _order = 'sequence,name desc'

    sequence = fields.Integer(string='Sequence')