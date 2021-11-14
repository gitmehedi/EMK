from odoo import fields, models, api


class InheritedSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _description = 'Description'

    salary_rule_id = fields.Many2one(comodel_name='cc.top.sheet.salary.rule.configuration', ondelete='cascade', string='Cost Center Report Salary Rule Configuration',
                                        store="True")
