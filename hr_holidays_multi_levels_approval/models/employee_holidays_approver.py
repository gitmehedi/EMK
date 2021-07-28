#-*- coding:utf-8 -*-

from odoo import models, fields

class EmployeeHolidaysApprover(models.Model):
    _name = "hr.employee.holidays.approver"
    _order= "sequence"
    
    employee = fields.Many2one('hr.employee', string='Employee', required=True,ondelete="cascade",)
    approver = fields.Many2one('hr.employee', string='Approver', required=True,ondelete="cascade",)
    sequence = fields.Integer(string='Approver sequence', default=10, required=True)
    