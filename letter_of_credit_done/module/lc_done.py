from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class LCEvaluationLine(models.Model):
    _name='lc.evaluation.line'
    _description = 'LC Done Criteria lines'
    _order = "seq asc"

    rel_job_id = fields.Many2one('letter.credit')
    seq = fields.Integer(string = 'Sequence')
    name = fields.Char(string = 'Criteria Name')
    marks = fields.Float(string = 'Total Marks')
    obtain_marks = fields.Float(string = 'Obtain Marks')
    comment = fields.Text(string='Comments')

    @api.constrains('obtain_marks')
    def _check_obtain_marks(self):
        for criteria_line in self:
            if criteria_line.obtain_marks>criteria_line.marks:
                raise ValidationError(_("Obtain marks can not be greater then total marks"))

