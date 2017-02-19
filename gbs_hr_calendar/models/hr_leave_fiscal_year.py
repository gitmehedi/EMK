# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class hr_leave_fiscalyear(models.Model):
    _name = "hr.leave.fiscal.year"
    _description = "HR Leave Fiscal Year"
    _order = "date_start, id"
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', size=6, required=True)
    date_start = fields.Date('Start Date', required=True)
    date_stop = fields.Date('End Date', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, 
                                 default= lambda self: self.env.user.company_id.id)
    
    state = fields.Selection([('draft','Open'), ('done','Closed')], default='draft')
    
    @api.one
    @api.constrains('name','code','company_id','date_start','date_stop')
    def check_leave_year_name(self):
         
        if self.name and self.company_id:
            filters = [['company_id', '=', self.company_id.id],
                       ['name', '=ilike', self.name]]
            leave_year_name = self.search(filters)
            if len(leave_year_name) > 1:
                raise Warning('[Leave Year Name] There can not be two leave year with same company.')
    
        if self.code and self.company_id:
            filters = [['company_id', '=', self.company_id.id],
                       ['code', '=ilike', self.code]]
            leave_year_code = self.search(filters)
            if len(leave_year_code) > 1:
                raise Warning('[Leave Year Code] There can not be two leave year code with same company.')
            
    def action_done(self):
        self.state = 'done'
