from odoo import api, fields, models


class HrDepartmentInherit(models.Model):
    _inherit = ['hr.department']

    approved_no_of_emp = fields.Integer(string='No. of Approved Employee',track_visibility='onchange')