from openerp import fields, models

class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    tax = fields.Char(string='Blood Group')
