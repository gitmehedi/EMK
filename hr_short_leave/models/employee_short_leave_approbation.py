#-*- coding:utf-8 -*-
from odoo import models, fields

class EmployeeShortLeaveApprobation(models.Model):
    _name = "hr.employee.short.leave.approbation"
    _order= "sequence"
    
    short_leave_ids = fields.Many2one('hr.short.leave', string='Short Leave', required=True,ondelete="cascade")
    approver = fields.Many2one('res.users', string='Approver', required=True,ondelete="cascade")
    sequence = fields.Integer(string='Approbation sequence', default=10, required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now())