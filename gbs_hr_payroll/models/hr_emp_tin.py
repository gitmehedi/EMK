from openerp import fields, models

class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    tin_req= fields.Boolean(string='TIN Applicable')
    tin = fields.Char(string = 'TIN')
