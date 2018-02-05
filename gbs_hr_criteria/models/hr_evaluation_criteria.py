from odoo import fields, models, api,_
from odoo.exceptions import UserError


class HREvaluationCriteria(models.Model):
    _name='hr.evaluation.criteria'
    _description = 'Evaluation Criteria'
    _order = "seq asc"

    seq = fields.Integer(string = 'Sequence',required=True)
    name = fields.Char(string = 'Criteria Name',required=True)
    marks = fields.Float(string = 'Marks',required=True,default=10)
    type = fields.Selection([
        ('pfevaluation','Performance Evaluation'),
        ('jobconf','Job Confirmation')
    ],required=True)
    is_active = fields.Boolean(string = 'Active')

    _sql_constraints = [
        ('name_uniq', 'unique (name,seq)', 'The name and sequence of the criteria must be unique!')
    ]