from odoo import api, fields, models

class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def check_1st_level_approval(self, employee):

        return False