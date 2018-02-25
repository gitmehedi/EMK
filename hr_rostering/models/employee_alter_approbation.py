#-*- coding:utf-8 -*-

from odoo import models, fields

class EmployeeAlterApprobation(models.Model):
    _name = "hr.employee.alter.approbation"
    _order= "sequence"
    
    alter_ids = fields.Many2one('hr.shift.alter', string='Alter', required=True,ondelete="cascade")
    approver = fields.Many2one('res.users', string='Approver', required=True,ondelete="cascade")
    sequence = fields.Integer(string='Approbation sequence', default=10, required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now())