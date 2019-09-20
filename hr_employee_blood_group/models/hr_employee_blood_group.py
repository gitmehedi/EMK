from odoo import fields, models

class HrEmployee(models.Model):

    _inherit = 'hr.employee'
    _description = "Employee Blood Group"

    blood= fields.Selection([
        ('a-', 'A-'),
        ('a+', 'A+'),
        ('b-', 'B-'),
        ('b+', 'B+'),
        ('o-', 'O-'),
        ('o+', 'O+'),
        ('ab-', 'AB-'),
        ('ab+','AB+')],
        string='Blood Group')
