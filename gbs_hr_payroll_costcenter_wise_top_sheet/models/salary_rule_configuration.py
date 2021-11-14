from odoo import fields, models, api


class SalaryRuleConfiguration(models.Model):
    _name = 'cc.top.sheet.salary.rule.configuration'
    _description = 'Salary Rule Configuration for Cost Center Wise Top Sheet'

    salary_rules = fields.One2many('hr.salary.rule', 'salary_rule_id',
                                        string="""Salary Rules""")

