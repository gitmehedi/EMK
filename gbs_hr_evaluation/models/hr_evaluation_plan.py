from odoo import fields, models, api,_
from datetime import datetime


class HREvaluationPlan(models.Model):
    _name='hr.evaluation.plan'
    _description = 'Employee Evaluation Plan'
    _order = "plan_year desc"

    name = fields.Char(string='Name', required=True,default='New')
    plan_year = fields.Selection([(num, str(num)) for num in range(2016, (datetime.now().year)+1 )],
                                 string='Plan Year',required=True)
    evaluation_form_ids = fields.One2many('hr.performance.evaluation','rel_plan_id')



class HREvaluationCriteria(models.Model):
    _name='hr.evaluation.criteria'
    _description = 'Evaluation Criteria'
    _order = "seq asc"

    seq = fields.Integer(string = 'Sequence',required=True)
    name = fields.Char(string = 'Criteria Name',required=True)
    marks = fields.Float(string = 'Marks',required=True,default=10)
    is_active = fields.Boolean(string = 'Active')
