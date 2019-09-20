from odoo import fields, models, api,_
from odoo.exceptions import UserError


class HREvaluationPlan(models.Model):
    _name='hr.evaluation.plan'
    _inherit = ['mail.thread']
    _description = 'Employee Evaluation Plan'
    _order = "plan_year desc"

    name = fields.Char(string='Name', required=True)
    plan_year = fields.Many2one('date.range', string="Plan Year", required=True)
    company_id = fields.Many2one('res.company', string='Company', required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )
    evaluation_form_ids = fields.One2many('hr.performance.evaluation','rel_plan_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], string='Status', default='draft', track_visibility='onchange')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the evaluation plan must be unique!')
    ]

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            self.operating_unit_id = []
            return {'domain': {'operating_unit_id': [('company_id','=', self.company_id.id)]}}

    @api.multi
    def action_confirm(self):
        pool_criteria_emp = self.env['hr.evaluation.criteria.line']
        for i in self.evaluation_form_ids:
            for criteria in self.env['hr.employee.criteria'].search([('is_active','=',True),('type','=','pfevaluation')]):
                criteria_res = {
                    'seq': criteria.seq,
                    'name': criteria.name,
                    'marks': criteria.marks,
                    'rel_evaluation_id': i.id,
                }
                pool_criteria_emp += self.env['hr.evaluation.criteria.line'].create(criteria_res)
        self.state = 'confirm'

    ####################################################
    # Override methods
    ####################################################

    @api.multi
    def unlink(self):
        for m in self:
            if m.state != 'draft':
                raise UserError(_('You can not delete in this state.'))
        return super(HREvaluationPlan, self).unlink()


