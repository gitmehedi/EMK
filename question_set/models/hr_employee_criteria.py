from odoo import fields, models, api,_
from odoo.exceptions import ValidationError


class HREvaluationCriteria(models.Model):
    _name='hr.employee.criteria'
    _description = 'Employee Criteria'
    _order = "seq asc"

    seq = fields.Integer(string = 'Sequence',required=True)
    name = fields.Char(string = 'Question',required=True)
    marks = fields.Float(string = 'Marks',required=True,default=10)
    type = fields.Selection([
        ('pfevaluation','Performance Evaluation'),
        ('jobconf','Job Confirmation'),
        ('lc_evaluation','LC Evaluation')
    ],required=True)
    is_active = fields.Boolean(string = 'Active')

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['hr.employee.criteria'].search([('name', '=', self.name),('type','=', self.type)])
        if len(name) > 1 :
            raise ValidationError('Unique Error] Name must be unique!')
