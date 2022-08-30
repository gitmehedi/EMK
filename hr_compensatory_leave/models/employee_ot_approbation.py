#-*- coding:utf-8 -*-

from odoo import models, fields

class EmployeeOTApprobation(models.Model):
    _name = "hr.employee.ot.approbation"
    _order= "sequence"
    
    ot_ids = fields.Many2one('hr.ot.requisition', string='Over Time', required=True,ondelete="cascade")
    approver = fields.Many2one('res.users', string='Approver', required=True,ondelete="cascade")
    sequence = fields.Integer(string='Approbation sequence', default=10, required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now())