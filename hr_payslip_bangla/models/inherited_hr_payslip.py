from odoo import fields, models, api


class InheritedHRSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    bangla_name = fields.Char(string="Bangla Name")

class InheritedHRDepartment(models.Model):
    _inherit = 'hr.department'

    bangla_name = fields.Char(string="Bangla Name")

class InheritedHRDesignation(models.Model):
    _inherit = 'hr.job'

    bangla_name = fields.Char(string="Bangla Name")


class InheritedHREmployee(models.Model):
    _inherit = 'hr.employee'

    bangla_name = fields.Char(string="Bangla Name")

